# Planwith

**Claude와 Codex가 서로 검토하고, 근거 있는 평점과 기획 문서를 남기는 로컬 스킬.**

API 키나 SDK 없이 로그인된 공식 CLI를 사용합니다. 현재 대화의 AI가 진행자가 되고,
상대 CLI를 호출합니다. 별도 서버나 상시 실행 프로세스는 없습니다.

## 설치

필수: Git, Python 3.9+, 공식 Claude Code와 Codex CLI, 각 기기에서 구독 계정 로그인.

```sh
git clone https://github.com/Jang-zn/planwith.git
cd planwith
./install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/Jang-zn/planwith.git
cd planwith
.\install.ps1
```

PowerShell 정책으로 스크립트가 차단되면 `py -3 install.py`를 실행하세요.
설치 후 새 CLI 세션을 여세요. 설치는 모델을 호출하지 않습니다.
기존 글로벌 지침을 보존하며 관리 블록만 추가하고, 최초 원본은 `.pre-planwith`로 백업합니다.
기존의 다른 `planwith` 스킬은 덮어쓰지 않습니다. 재설치는 멱등적으로 갱신합니다.
`CODEX_HOME`, `CLAUDE_CONFIG_DIR`가 있으면 해당 경로를 따릅니다.

## 사용

작업할 프로젝트에서 Claude 또는 Codex를 실행한 뒤:

> 코덱스랑 주식 자동매매 서비스 기획해봐. 산출물은 docs에 남겨.

> 클로드랑 기존 기획의 타겟과 BM 다시 검토해봐.

Claude에서는 `/planwith`, Codex에서는 `$planwith`로 명시적으로 요청할 수도 있습니다.
자연어 선택은 모델 동작에 따라 누락될 수 있습니다. 명시적 호출을 대안으로 사용하세요.

## 문서 저장 경로

Claude와 Codex 모두 **CLI를 실행한 작업 폴더의 `docs/`**에 문서를 저장합니다.
CLI에서 작업 폴더를 명시적으로 선택했다면 그 폴더를 사용합니다. Git 최상위 루트를
자동으로 찾거나 스킬 설치 폴더에 저장하지 않습니다. 저장 경로를 생략해도 질문 없이
이 기본값을 사용하며, 기획명 하위 폴더를 임의로 추가하지 않습니다.

예: `/projects/my-app/frontend`에서 실행했다면 `/projects/my-app/frontend/docs/`입니다.
두 CLI를 같은 폴더에서 실행하면 저장 위치도 같습니다. 다른 폴더에서 실행하면 달라집니다.
처음 확정한 작업 폴더를 상대 CLI에도 전달하므로, 진행 중 `cd`해도 저장 위치는 바뀌지 않습니다.
사용자가 다른 경로를 지정하면 우선 적용하며, 상대경로는 처음 작업 폴더 기준입니다.
작업 폴더를 알 수 없거나 명시적 경로 지시가 충돌할 때만 먼저 질문하고 기다립니다.
현재 실행기는 프로젝트 내부 경로만 지원합니다. 외부 경로 요청은 설명 후 다시 확인합니다.

## 결과

기본 산출물 구조입니다.

```text
your-project/docs/
├── README.md
├── 00-brief.md
├── decisions.md
├── open-questions.md
├── sources.md
├── ... 타겟·제품·운영·디자인·설계·검증 문서
└── discussions/
    ├── README.md
    └── 001-target/
        ├── discussion.md   # 평가표 + 안건별 전체 논의 + 사용자 답변
        └── state.json      # 재개 가능한 예산·단계 상태
```

같은 안건 안에서 두 모델의 발언을 함께 관리합니다. 다른 PC에서도 프로젝트를 커밋·푸시한 뒤
풀하면 문서와 상태를 읽고 이어갑니다. 특정 기기의 CLI 세션 ID에 의존하지 않습니다.
동일 안건을 여러 기기에서 동시에 진행하지 마세요. Git 충돌은 먼저 해결해야 합니다.

## 토론과 심판

독립 제안 → 상호 비판 → 수정 → 새 세션의 심판 → 필요시 마지막 공방 → 종료.
심판은 목표 적합성·근거·실행 가능성·비용/위험·반박 대응력을 각각 0–5점으로 평가하고
점수 근거·한계·재평가 조건을 남깁니다. 근거가 없으면 판단 불가이며 성공 확률로 해석하지 않습니다.
AI 권고와 사용자 승인을 구분합니다. 필요한 결정은 현재 대화에서 질문하고 답변 후 재개합니다.

안건당 외부 호출 8회, 누적 실행 30분, 기본 호출 5분. 공방 최대 2회.
한 번의 요청은 중요 안건 최대 3개; 나머지는 대기 목록에 둡니다.
스크립트는 안건 예산·단계·입력 대기를 강제하고, 진행 스킬은 전체 안건 수와 심판의 의미적
종료 조건을 관리합니다. 자동 재시도·API 대체·자동 커밋은 없습니다.

## 구독과 도구 제한

실행 전 구독 로그인 상태를 확인합니다. API 키/제공자 환경변수가 설정되면 실행을 거절합니다.
Codex는 사용자 모델 설정을 건너뛰고 read-only sandbox로 실행합니다.
Claude 참여자는 도구와 MCP를 비활성화합니다. 자료 조사와 파일 작성은 진행자가 맡습니다.
CLI 구독 한도는 적용됩니다. Claude `--bare`는 구독 인증을 쓰지 않으므로 사용하지 않습니다.

CLI 동작과 관리형 설정은 버전에 따라 달라질 수 있습니다. 최초 확인 환경:
macOS, Codex 0.160.0, Claude Code 2.1.289. Windows 설치/로직은 CI 대상이며
실제 Windows 구독 로그인 실행은 별도 확인이 필요합니다.

## 업데이트 / 제거

`git pull` 후 설치 명령을 다시 실행하세요.

```sh
python3 install.py --uninstall
```

Windows에서는 `py -3 install.py --uninstall`. 도구가 설치한 스킬과 관리 블록만 제거하며,
프로젝트 문서는 삭제하지 않습니다.

## 개발 및 검증

```sh
python3 -m unittest discover -s tests -v
```

Python 표준 라이브러리만 사용합니다. 테스트는 실제 모델을 호출하지 않습니다.
실제 호출은 설치된 skill/scripts/peer.py의 `--help`를 참고하세요.
진행 상태가 비정상 종료로 잠긴 경우 실행 중인 프로세스가 없는 것을 확인한 후
해당 안건의 `.planwith.lock`만 제거합니다. `state.json`은 예산 초기화를 위해 삭제하지 마세요.

공식 참고: [Codex 비대화형 실행](https://learn.chatgpt.com/docs/non-interactive-mode),
[Claude 비대화형 실행](https://code.claude.com/docs/en/headless).
