import os
import sys
from dotenv import load_dotenv

load_dotenv('/Users/sseung/Documents/business/Bapmap/.env')

from supabase import create_client
from generator import generate_post

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# 메모는 있는데 content가 없는 스팟만
res = sb.table('spots').select('*').execute()
spots = [s for s in res.data if s.get('memo') and s.get('memo').strip() and not s.get('content')]

if not spots:
    print("생성할 스팟 없음 (메모 있고 content 없는 업로드완료 스팟)")
    sys.exit()

print(f"총 {len(spots)}개 생성 예정\n")

for spot in spots:
    name = spot.get('english_name') or spot['name']
    print(f"생성 중: {name}...")
    try:
        content = generate_post(spot)
        sb.table('spots').update({'content': content, 'status': '업로드완료'}).eq('id', spot['id']).execute()
        print(f"  ✓ 완료\n")
    except Exception as e:
        print(f"  ✗ 실패: {e}\n")
