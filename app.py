import streamlit as st

from utils.data_manager import (
    format_commit_message,
    get_random_question,
    load_questions,
    save_notes,
    save_solution,
    update_status,
)
from utils.git_helper import git_add_commit, git_push


st.set_page_config(page_title="LeetCode Hunter 🎯", page_icon="🎯", layout="centered")
st.title("LeetCode Hunter 🎯")

questions = load_questions()
total = len(questions)
solved = sum(1 for q in questions if q.get("status") == "solved")
progress = solved / total if total else 0

with st.sidebar:
    st.subheader("进度")
    st.progress(progress)
    st.caption(f"已完成 {solved}/{total}")

    solved_questions = [q for q in questions if q.get("status") == "solved"]
    solved_titles = [
        f"{q.get('id')} - {q.get('title')}" for q in solved_questions
    ]
    selected_review = st.selectbox(
        "复习已完成题目",
        options=["(选择题目)"] + solved_titles,
        index=0,
    )

    if selected_review != "(选择题目)":
        selected_index = solved_titles.index(selected_review)
        st.session_state.current_question = solved_questions[selected_index]
        st.session_state.code_input = ""
        st.session_state.notes_input = ""

    if st.button("⬆️ Git Push", use_container_width=True):
        push_result = git_push()
        if push_result.returncode != 0:
            st.error(push_result.stderr.strip() or "Git push 失败。")
        else:
            st.success("已推送到远端。")

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "code_input" not in st.session_state:
    st.session_state.code_input = ""

if "notes_input" not in st.session_state:
    st.session_state.notes_input = ""

if st.button("🎲 随机抽取一道题", use_container_width=True):
    question = get_random_question()
    st.session_state.current_question = question
    st.session_state.code_input = ""
    st.session_state.notes_input = ""
    if question is None:
        st.info("全部题目已完成，恭喜！")

question = st.session_state.current_question

if question:
    st.markdown(f"### [{question.get('title')}]({question.get('url')})")
    st.write(f"**难度：** {question.get('difficulty')}")
    st.write(f"**Tags：** {' / '.join(question.get('tags', []))}")

    with st.expander("💡 查看算法锦囊"):
        st.write(question.get("pattern_hint", ""))

    st.text_area("代码", height=240, key="code_input")
    st.text_area("笔记", height=140, key="notes_input")
    mark_best = st.checkbox("标记为 best 解法（覆盖同题最佳）", value=False)

    if st.button("提交 ✅"):
        updated = update_status(
            question_id=question.get("id"),
            code=st.session_state.code_input,
            notes=st.session_state.notes_input,
        )
        if updated is None:
            st.error("更新失败，请检查题目 ID。")
        else:
            solution_path = save_solution(
                question_id=question.get("id"),
                title=question.get("title", ""),
                code=st.session_state.code_input,
                is_best=mark_best,
            )
            notes_path = save_notes(
                question_id=question.get("id"),
                title=question.get("title", ""),
                notes=st.session_state.notes_input,
            )
            commit_paths = ["data/problems.json", str(solution_path)]
            if notes_path is not None:
                commit_paths.append(str(notes_path))
            commit_result = git_add_commit(
                paths=commit_paths,
                message=format_commit_message(
                    question_id=question.get("id"),
                    title=question.get("title", ""),
                ),
            )
            if commit_result.returncode != 0:
                st.warning(commit_result.stderr.strip() or "Git commit 失败。")
            st.balloons()
            st.success("已保存，继续加油！")
            st.session_state.current_question = updated
            st.rerun()
elif total == 0:
    st.warning("暂未找到题目数据，请检查 data/problems.json。")
else:
    st.info("点击上方按钮开始抽题。")
