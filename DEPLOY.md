# 배포 매뉴얼

배포는 **사내 서버에서** 진행합니다.

---

## 일반 업데이트 (코드 변경 시)

```bash
# 1. 프로젝트 디렉토리로 이동
cd /path/to/work-management

# 2. 최신 코드 받기
git pull origin feat/login-notification

# 3. 배포 실행
sudo bash deploy.sh
```

완료 후 터미널에 출력된 접속 주소(`http://서버IP:8080`)로 확인합니다.

---

## 최초 배포 시 추가 작업

처음 배포할 때는 **관리자 계정을 먼저 만들어야** 합니다.  
로그인 기능이 있어서 계정 없이는 시스템을 사용할 수 없습니다.

```bash
# deploy.sh 실행 후에 아래 명령 실행
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_admin.py
```

프롬프트에서 사용자명·이름·비밀번호를 입력하면 관리자 계정이 생성됩니다.

### 파트원 계정 일괄 생성 (선택)

`backend/staff_accounts.json` 파일을 편집한 뒤 실행합니다.

```bash
cd /var/www/okr-app/backend
DATA_DIR=/var/www/okr-app/data .venv/bin/python create_staff_accounts.py
```

> 생성된 계정은 첫 로그인 시 비밀번호 변경을 요구합니다. 파트원들에게 임시 비밀번호를 안내해 주세요.

---

## 참고

### 배포 기본값

| 항목 | 값 |
|------|-----|
| 배포 경로 | `/var/www/okr-app` |
| 데이터(DB·업로드) 경로 | `/var/www/okr-app/data` |
| 기본 포트 | `8080` |
| 서비스 이름 | `okr-app` |

포트를 변경하려면 인자를 추가합니다.

```bash
sudo bash deploy.sh 9090
```

### 서비스 관리

```bash
# 상태 확인
sudo systemctl status okr-app

# 재시작
sudo systemctl restart okr-app

# 실시간 로그
sudo journalctl -u okr-app -f
```
