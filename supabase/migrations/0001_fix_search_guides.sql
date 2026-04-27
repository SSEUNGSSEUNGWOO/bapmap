-- 0001: search_guides RPC 복구
--
-- 배경:
--   기존 search_guides RPC는 옛날 스키마(area/content/type/sources/embedding) 기반.
--   현재 guides 테이블은 새 스키마(body/category_tag/spot_slugs)이고 embedding 컬럼 자체가 없어서
--   RPC 호출 시 "column \"area\" does not exist" 에러로 실패 중이었다.
--
-- 변경:
--   1. guides 테이블에 embedding 컬럼(vector 1536) + HNSW 인덱스 추가
--      (hybrid_search_spots 와 동일하게 OpenAI text-embedding-3-small 사용)
--   2. search_guides RPC 재작성:
--      - 새 컬럼 사용 (body, category_tag, spot_slugs)
--      - frontend 호환을 위해 alias 반환 (content / type / sources)
--      - status='published' + embedding NOT NULL 가드 추가

-- 1. embedding 컬럼 + HNSW 인덱스
ALTER TABLE guides ADD COLUMN IF NOT EXISTS embedding vector(1536);

CREATE INDEX IF NOT EXISTS guides_embedding_idx
  ON guides USING hnsw (embedding vector_cosine_ops);

-- 2. search_guides RPC 재작성
--    기존 함수의 RETURNS TABLE 시그니처가 달라서 (area 컬럼 포함)
--    CREATE OR REPLACE로는 변경 불가 → DROP 후 재생성
DROP FUNCTION IF EXISTS public.search_guides(vector, double precision, integer);

CREATE FUNCTION public.search_guides(
  query_embedding vector,
  match_threshold double precision,
  match_count integer
)
RETURNS TABLE(
  id uuid,
  title text,
  slug text,
  content text,        -- alias for body (frontend g.content)
  type text,           -- alias for category_tag (frontend g.type)
  sources text[],      -- alias for spot_slugs (frontend g.sources)
  similarity double precision
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    id,
    title,
    slug,
    body AS content,
    category_tag AS type,
    spot_slugs AS sources,
    1 - (embedding <=> query_embedding) AS similarity
  FROM guides
  WHERE status = 'published'
    AND embedding IS NOT NULL
    AND 1 - (embedding <=> query_embedding) > match_threshold
  ORDER BY embedding <=> query_embedding
  LIMIT match_count;
$$;
