# 배포 방법
- 로컬 환경에서 docker 환경 확인
- web이 아닌 repo 디렉토리 경로에서 실행
- vpn 연결 상태 확인 및 kubectl context를 pgmlops-01로 설정 필요
```bash
docker build --platform linux/amd64 \
       -f web/Dockerfile
       -t harbor.bluewhale.kr:31013/smartagent/web:latest .
docker push harbor.bluewhale.kr:31013/smartagent/web:latest 
kubectl rollout restart deployment web -n naver-rlhf
```
