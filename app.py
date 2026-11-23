import streamlit as st
import random
from collections import deque

st.set_page_config(page_title="전력 배달 레이스", page_icon="⚡")

SIZE = 6
START = (0, 0)
GOAL = (5, 5)

st.title("⚡ 전력 배달 레이스")
st.write("🤖 로봇을 움직여 배터리 3개를 모으고 목적지에 도착하세요!")

# 게임 초기 설정
if "level" not in st.session_state:
    st.session_state.level = 1
    st.session_state.lives = 3
    st.session_state.score = 0
    st.session_state.player = START
    st.session_state.game_over = False


# 이동 가능한 장소 찾기
def find_path(obstacles):
    visited = {START}
    queue = deque([START])

    while queue:
        r, c = queue.popleft()

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            pos = (nr, nc)

            if (0 <= nr < SIZE and 0 <= nc < SIZE
                and pos not in obstacles and pos not in visited):
                visited.add(pos)
                queue.append(pos)

    return visited


# 랜덤 맵 생성
def make_map():
    level = st.session_state.level
    probability = min(0.12 + level * 0.045, 0.42)

    while True:
        obstacles = set()

        for r in range(SIZE):
            for c in range(SIZE):
                pos = (r, c)

                if pos not in [START, GOAL]:
                    if random.random() < probability:
                        obstacles.add(pos)

        reachable = find_path(obstacles)

        if GOAL in reachable and len(reachable) >= 5:
            break

    possible = list(reachable - {START, GOAL})
    batteries = set(random.sample(possible, 3))

    st.session_state.obstacles = obstacles
    st.session_state.batteries = batteries
    st.session_state.player = START


# 첫 맵 생성
if "obstacles" not in st.session_state:
    make_map()


# 방향 이동
def move(dr, dc):
    if st.session_state.game_over:
        return

    r, c = st.session_state.player
    nr, nc = r + dr, c + dc
    pos = (nr, nc)

    if not (0 <= nr < SIZE and 0 <= nc < SIZE):
        return

    if pos in st.session_state.obstacles:
        st.session_state.lives -= 1

        if st.session_state.lives <= 0:
            st.session_state.game_over = True
        return

    st.session_state.player = pos

    # 배터리 획득
    if pos in st.session_state.batteries:
        st.session_state.batteries.remove(pos)
        st.session_state.score += 100

    # 목적지 도착
    if pos == GOAL and len(st.session_state.batteries) == 0:
        st.session_state.score += 300
        st.session_state.level += 1
        make_map()


# 정보 표시
a, b, c = st.columns(3)

a.metric("스테이지", f"{st.session_state.level}")
b.metric("목숨", "❤️ " * st.session_state.lives)
c.metric("점수", st.session_state.score)

st.divider()

st.subheader("🗺️ 게임 맵")

st.write("🤖 로봇  ⚡ 배터리  🧱 장애물  🏁 목적지")

# 맵 출력
for r in range(SIZE):
    cols = st.columns(SIZE)

    for c in range(SIZE):
        pos = (r, c)

        if pos == st.session_state.player:
            icon = "🤖"
        elif pos in st.session_state.batteries:
            icon = "⚡"
        elif pos == GOAL:
            icon = "🏁"
        elif pos in st.session_state.obstacles:
            icon = "🧱"
        else:
            icon = "⬜"

        cols[c].button(
            icon,
            key=f"map_{r}_{c}_{st.session_state.level}",
            disabled=True,
            use_container_width=True
        )

st.divider()

st.subheader("🎮 로봇 조작")

st.write("방향 버튼을 눌러 로봇을 움직이세요!")

# 이동 버튼
col1, col2, col3 = st.columns(3)

with col2:
    if st.button("⬆️", use_container_width=True,
                 disabled=st.session_state.game_over):
        move(-1, 0)
        st.rerun()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️", use_container_width=True,
                 disabled=st.session_state.game_over):
        move(0, -1)
        st.rerun()

with col2:
    if st.button("⬇️", use_container_width=True,
                 disabled=st.session_state.game_over):
        move(1, 0)
        st.rerun()

with col3:
    if st.button("➡️", use_container_width=True,
                 disabled=st.session_state.game_over):
        move(0, 1)
        st.rerun()


# 게임 결과
if st.session_state.game_over:
    st.error("💥 게임 오버! 목숨을 모두 잃었습니다.")

    if st.button("🔄 다시 시작"):
        for key in ["level", "lives", "score",
                    "player", "game_over", "obstacles",
                    "batteries"]:
            del st.session_state[key]

        st.rerun()

elif st.session_state.player == GOAL:
    if len(st.session_state.batteries) == 0:
        st.success("🎉 스테이지 클리어!")
    else:
        st.warning("배터리를 모두 모아야 목적지에 도착할 수 있어요!")

st.caption("⚡ 전기전자 원리: 배터리의 에너지 저장과 전력 공급 개념을 활용한 게임입니다.")
