# GitHub Pages 배포 순서

## 1. GitHub에서 새 저장소 만들기

1. https://github.com/new 접속
2. Repository name: `qpesk-juse-redesign`
3. Public 선택
4. `Add a README file` 체크하지 않기
5. `Create repository` 클릭

## 2. 로컬에서 GitHub 저장소 연결

GitHub에서 저장소를 만들면 아래처럼 주소가 보입니다.

```text
https://github.com/내아이디/qpesk-juse-redesign.git
```

그 주소를 사용해 다음 명령을 실행합니다.

```powershell
git remote add origin https://github.com/내아이디/qpesk-juse-redesign.git
git push -u origin main
```

## 3. GitHub Pages 켜기

1. GitHub 저장소 페이지로 이동
2. `Settings`
3. 왼쪽 메뉴 `Pages`
4. `Build and deployment`에서 Source를 `Deploy from a branch`로 선택
5. Branch: `main`, Folder: `/root` 선택
6. `Save`

잠시 후 아래 형태의 주소가 생깁니다.

```text
https://내아이디.github.io/qpesk-juse-redesign/
```
