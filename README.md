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

Claude와 Codex 모두 **CLI를 실행한 작업 폴더의 `docs/round-NNN/`**에 문서를 저장합니다.
CLI에서 작업 폴더를 명시적으로 선택했다면 그 폴더를 사용합니다. Git 최상위 루트를
자동으로 찾거나 스킬 설치 폴더에 저장하지 않습니다. 저장 경로를 생략해도 질문 없이
이 기본값을 사용하며, 기획명 하위 폴더를 임의로 추가하지 않습니다.

예: `/projects/my-app/frontend`에서 실행했다면 `/projects/my-app/frontend/docs/round-001/`입니다.
두 CLI를 같은 폴더에서 실행하면 저장 위치도 같습니다. 다른 폴더에서 실행하면 달라집니다.
처음 확정한 작업 폴더를 상대 CLI에도 전달하므로, 진행 중 `cd`해도 저장 위치는 바뀌지 않습니다.
사용자가 다른 경로를 지정하면 우선 적용하며, 상대경로는 처음 작업 폴더 기준입니다.
작업 폴더를 알 수 없거나 명시적 경로 지시가 충돌할 때만 먼저 질문하고 기다립니다.
현재 실행기는 프로젝트 내부 경로만 지원합니다. 외부 경로 요청은 설명 후 다시 확인합니다.

## 결과

기본 산출물 구조입니다.

```text
your-project/docs/round-001/
├── conclusion-report.html  # 사용자가 읽는 결론 보고서
└── records/                # 에이전트 재검토·이어가기용 기록
    ├── round.json
    ├── README.md
    ├── 00-brief.md
    ├── decisions.md
    ├── open-questions.md
    ├── sources.md
    ├── ... 타겟·제품·운영·디자인·설계·검증 문서
    └── discussions/
        ├── README.md
        └── 001-target/
            ├── discussion.md
            └── state.json
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

## 결론 보고용 HTML

각 기획 실행 종료 시 `docs/round-NNN/conclusion-report.html`을 생성·갱신합니다. 이번 라운드뿐 아니라
기존 전체 안건의 결론, 심판 평점과 근거, 사용자 승인 여부, 미결정 사항, 다음 행동을 포함합니다.
중단·질문 대기 상태도 숨기지 않습니다. 원문 MD는 보존하고 보고서에서 연결합니다.

디자인은 밝은 배경, 절제된 색상, 얇은 구분선과 충분한 여백을 사용하는 플랫 스타일입니다.
비교표, 평점 막대, 흐름도, 화면 예시 등을 내용에 맞게 구성합니다. Chart.js, Three.js,
이미지 생성 등도 필요한 경우 사용하되 핵심 내용은 네트워크나 JavaScript 없이도 읽을 수 있게 합니다.
완료 후 호스트의 미리보기에서 열거나 파일 링크를 제공합니다.

보고서 작성 시 [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)의 쉬운 설명과
[NomaDamas/k-skill korean-humanizer](https://github.com/NomaDamas/k-skill/tree/main/korean-humanizer)의
한국어 윤문 지침을 적용합니다. `k-윤문`이라는 정확한 이름 대신 확인한 k-skill의 윤문 스킬을
사용합니다. 원본 지침·고정 커밋·MIT 라이선스를 `skill/references/editorial/`에 동봉하여
추가 설치 없이 두 환경에서 함께 사용합니다. 외부 CLI 업데이트 지시는 실행하지 않습니다.
문체는 사용자 지정에 따라 `~함`, `~임`, `~필요` 또는 명사형 종결을 사용합니다.
독자는 비전문가 성인으로 설정하고 쉬운 표현 때문에 근거·수치·불확실성을 바꾸지 않습니다.

## 아이디어 구체화와 반복 라운드

아이디어 구체화 → 논의·평가·보고서 → 사용자 피드백 → 다시 구체화하는 흐름을 지원합니다.
`docs/planwith-rounds.md`에서 라운드별 보고서를 확인할 수 있습니다.

```text
docs/
├── planwith-rounds.md
├── round-001/
│   ├── conclusion-report.html
│   └── records/  # 이전 기획·토론·상태 보존
└── round-002/
    ├── conclusion-report.html
    └── records/
        ├── round.json
        ├── 00-brief.md
        ├── changes.md
        └── discussions/
```

안건 내부의 공방 1·2차와 기획 라운드는 별개입니다. 확인 질문에 답하거나 중단된 작업을
이어가는 경우 같은 라운드에서 갱신합니다. 결과를 토대로 새 방향으로 재기획하거나 다음
라운드를 요청하면 이전 라운드를 닫고 다음 번호를 생성합니다. 애매할 때만 이어가기인지
새 라운드인지 질문합니다. 새 라운드는 사용자 요청 없이 자동 반복하지 않습니다.

새 라운드에는 이전 결론·미해결점·새 제약과 변경 이유를 기록합니다. 그대로 유지하는 결론은
출처 라운드를 명시하며, 논의 기록과 호출 예산을 복사·초기화하지 않습니다. 이전 HTML·MD는
덮어쓰지 않습니다. 기본값은 운영체제 쓰기 잠금이 아닌 스킬의 보존 규칙이며, 사용자의 명시적
과거 문서 수정 요청이 있으면 변경 이력을 남깁니다. 기존 `docs/` 직하의 문서는 자동 이동하지
않고 첫 라운드의 참고 자료로 연결합니다.

사용자에게는 HTML 보고서를 기본으로 제시하며, 안건별 MD를 읽지 않아도 결론과 근거를
이해할 수 있게 작성합니다. 상세 MD와 실행 상태는 `records/`에 보존하여 다음 라운드의
재검토에 사용합니다. 이전 버전의 라운드 폴더는 자동 이동하지 않고 기존 경로로 읽습니다.
