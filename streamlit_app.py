import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(page_title="온가족 마블 주사위", layout="centered")

# 세션 초기화 함수
def reset_game():
    st.session_state.game_started = False
    st.session_state.players = []
    st.session_state.current_idx = 0
    st.session_state.total_rounds = 1
    st.session_state.target_rounds = 20
    st.session_state.double_count = 0 
    st.session_state.last_player_info = None
    st.session_state.dice = (1, 1)

if 'game_started' not in st.session_state:
    reset_game()

# CSS 스타일
st.markdown("""
    <style>
    .dice-container { display: flex; justify-content: center; gap: 15px; margin: 15px 0; }
    .die { 
        width: 70px; height: 70px; background-color: white; border: 3px solid #34495e;
        border-radius: 12px; display: flex; align-items: center; justify-content: center;
        font-size: 35px; font-weight: bold; color: #2c3e50;
    }
    .order-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 5px solid #2c3e50; margin-bottom: 20px; }
    .history-box { font-size: 1.1rem; color: #7f8c8d; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 설정 화면 ---
if not st.session_state.game_started:
    st.title("🎲 모두의 마블 주사위 도우미")
    target_r = st.number_input("목표 회차 설정", min_value=1, value=20)
    
    st.write("### 참여 인원 및 이름 입력")
    # 인원수를 선택하면 그만큼 입력창이 생깁니다.
    num_players = st.slider("참여 인원", min_value=2, max_value=4, value=4)
    
    # 색상을 다시 4가지로 고정했습니다.
    colors = {"파랑": "#3498db", "빨강": "#e74c3c", "초록": "#2ecc71", "노랑": "#f1c40f"}
    selected_info = []
    
    for i in range(num_players):
        c1, c2 = st.columns([2, 1])
        with c1:
            u_name = st.text_input(f"참여자 {i+1} 이름", value=f"플레이어 {i+1}", key=f"name_{i}")
        with c2:
            u_color = st.selectbox(f"색상 {i+1}", list(colors.keys()), index=i % len(colors), key=f"color_{i}")
        selected_info.append({"name": u_name, "color_pref": u_color})

    if st.button("🚀 게임 시작", use_container_width=True):
        final_p = []
        for info in selected_info:
            final_p.append({
                "name": info['name'] if info['name'].strip() != "" else f"플레이어 {selected_info.index(info)+1}", 
                "color": colors[info['color_pref']], 
                "island_fail_count": 0
            })
        
        random.shuffle(final_p) # 순서 랜덤 섞기
        st.session_state.players = final_p
        st.session_state.target_rounds = target_r
        st.session_state.game_started = True
        st.rerun()

# --- 게임 화면 ---
else:
    p = st.session_state.players[st.session_state.current_idx]
    
    order_text = " → ".join([f"**{pl['name']}**" for pl in st.session_state.players])
    st.markdown(f"<div class='order-box'><b>현재 순서:</b> {order_text}</div>", unsafe_allow_html=True)
    
    st.subheader(f"🚩 제 {st.session_state.total_rounds} / {st.session_state.target_rounds} 회차")

    is_in_island = p['island_fail_count'] > 0
    fail_msg = f" (탈출 시도: {p['island_fail_count']}회)" if is_in_island else ""
    st.markdown(f"""
        <div style="background-color:{p['color']}22; padding:15px; border-radius:10px; border:2px solid {p['color']}; text-align:center;">
            <h2 style="color:{p['color']}; margin:0;">{p['name']} 님 차례{fail_msg}</h2>
        </div>
    """, unsafe_allow_html=True)

    placeholder = st.empty()
    d1, d2 = st.session_state.dice
    placeholder.markdown(f"<div class='dice-container'><div class='die'>{d1}</div><div class='die'>{d2}</div></div>", unsafe_allow_html=True)

    if st.session_state.last_player_info:
        last = st.session_state.last_player_info
        st.markdown(f"<div class='history-box'>⬅️ <b>방금:</b> {last['name']} ({last['res']})</div>", unsafe_allow_html=True)

    def next_turn(result_text):
        st.session_state.last_player_info = {"name": p['name'], "res": result_text}
        st.session_state.double_count = 0 
        st.session_state.current_idx += 1
        if st.session_state.current_idx >= len(st.session_state.players):
            st.session_state.current_idx = 0
            st.session_state.total_rounds += 1
        if st.session_state.total_rounds > st.session_state.target_rounds:
            st.balloons()
            st.info("게임이 종료되었습니다!")
        else:
            st.rerun()

    def roll_animation():
        for _ in range(8):
            r1, r2 = random.randint(1, 6), random.randint(1, 6)
            placeholder.markdown(f"<div class='dice-container'><div class='die'>{r1}</div><div class='die'>{r2}</div></div>", unsafe_allow_html=True)
            time.sleep(0.08)
        return random.randint(1, 6), random.randint(1, 6)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎲 주사위", use_container_width=True, disabled=is_in_island):
            r1, r2 = roll_animation()
            st.session_state.dice = (r1, r2)
            
            if st.session_state.total_rounds == 1 and st.session_state.double_count == 0 and (r1 + r2 == 8):
                p['island_fail_count'] = 1 
                next_turn("8 무인도행 (다음 턴부터 탈출 시도)")
            
            elif r1 == r2:
                st.session_state.double_count += 1
                if st.session_state.double_count >= 3:
                    p['island_fail_count'] = 1 
                    next_turn("3더블 무인도행")
                else:
                    st.session_state.last_player_info = {"name": p['name'], "res": f"더블({r1}) 한 번 더!"}
                    st.rerun()
            else:
                next_turn(f"{r1+r2}칸 이동")

    with col2:
        if st.button("🏝️ 무인도", use_container_width=True):
            r1, r2 = roll_animation()
            st.session_state.dice = (r1, r2)
            current_attempt = p['island_fail_count']
            
            if r1 == r2:
                p['island_fail_count'] = 0 
                if current_attempt >= 3:
                    st.session_state.double_count = 1
                    st.session_state.last_player_info = {"name": p['name'], "res": f"3회차 더블({r1}) 탈출! 한 번 더!"}
                    st.rerun()
                else:
                    next_turn(f"더블({r1}) 탈출 성공! {r1+r2}칸 이동")
            
            elif current_attempt >= 3:
                p['island_fail_count'] = 0
                next_turn(f"3회 시도 완료! 강제 탈출로 {r1+r2}칸 이동")
            else:
                p['island_fail_count'] += 1
                next_turn(f"탈출 실패 (다음은 {p['island_fail_count']}회 시도)")

    with col3:
        if st.button("✈️ 세계여행", use_container_width=True, disabled=is_in_island):
            next_turn("세계여행 대기")

    st.markdown("---")
    if st.button("🔄 게임 초기화", type="primary", use_container_width=True):
        reset_game()
        st.rerun()
