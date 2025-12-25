import streamlit as st

from utils.data_manager import (
    clear_all_files,
    clear_question_files,
    format_commit_message,
    get_random_question,
    load_questions,
    read_notes,
    reset_all_questions,
    reset_question_data,
    save_notes,
    save_solution,
    update_status,
)
from utils.ai_client import call_openai_compatible, get_ai_config
from utils.git_helper import git_add_commit, git_push


st.set_page_config(page_title="LeetCode Hunter 🎯", page_icon="🎯", layout="centered")
st.title("LeetCode Hunter 🎯")

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "code_input" not in st.session_state:
    st.session_state.code_input = ""

if "notes_input" not in st.session_state:
    st.session_state.notes_input = ""

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

    st.divider()
    st.subheader("清零")
    if "confirm_clear_current" not in st.session_state:
        st.session_state.confirm_clear_current = False
    if "confirm_clear_all" not in st.session_state:
        st.session_state.confirm_clear_all = False

    clear_current_clicked = st.button("清空当前题目解法/笔记", use_container_width=True)
    if clear_current_clicked:
        st.session_state.confirm_clear_current = True

    if st.session_state.confirm_clear_current:
        st.warning("确认清空当前题目的所有解法与笔记？此操作不可恢复。")
        col_yes, col_no = st.columns(2)
        if col_yes.button("确认清空当前题目", use_container_width=True):
            if st.session_state.current_question is None:
                st.error("当前没有选中的题目。")
            else:
                current = st.session_state.current_question
                clear_question_files(
                    question_id=current.get("id"),
                    title=current.get("title", ""),
                )
                updated = reset_question_data(current.get("id"))
                from pathlib import Path

                Path("solutions").mkdir(exist_ok=True)
                Path("notes").mkdir(exist_ok=True)
                commit_result = git_add_commit(
                    paths=["data/problems.json", "solutions", "notes"],
                    message=f"Reset {current.get('id')} solutions",
                )
                if commit_result.returncode != 0:
                    st.warning(commit_result.stderr.strip() or "Git commit 失败。")
                push_result = git_push()
                if push_result.returncode != 0:
                    st.warning(push_result.stderr.strip() or "Git push 失败。")
                if updated is not None:
                    st.session_state.current_question = updated
                st.session_state.code_input = ""
                st.session_state.notes_input = ""
                st.session_state.confirm_clear_current = False
                st.success("已清空当前题目。")
                st.rerun()
        if col_no.button("取消", use_container_width=True):
            st.session_state.confirm_clear_current = False

    clear_all_clicked = st.button("清空全部解法/笔记", use_container_width=True)
    if clear_all_clicked:
        st.session_state.confirm_clear_all = True

    if st.session_state.confirm_clear_all:
        st.warning("确认清空所有题目的解法与笔记？此操作不可恢复。")
        col_yes, col_no = st.columns(2)
        if col_yes.button("确认清空全部", use_container_width=True):
            clear_all_files()
            reset_all_questions()
            from pathlib import Path

            Path("solutions").mkdir(exist_ok=True)
            Path("notes").mkdir(exist_ok=True)
            commit_result = git_add_commit(
                paths=["data/problems.json", "solutions", "notes"],
                message="Reset all solutions",
            )
            if commit_result.returncode != 0:
                st.warning(commit_result.stderr.strip() or "Git commit 失败。")
            push_result = git_push()
            if push_result.returncode != 0:
                st.warning(push_result.stderr.strip() or "Git push 失败。")
            st.session_state.current_question = None
            st.session_state.code_input = ""
            st.session_state.notes_input = ""
            st.session_state.confirm_clear_all = False
            st.success("已清空全部题目。")
            st.rerun()
        if col_no.button("取消", use_container_width=True):
            st.session_state.confirm_clear_all = False

if st.button("🎲 随机抽取一道题", use_container_width=True):
    question = get_random_question()
    st.session_state.current_question = question
    st.session_state.code_input = ""
    st.session_state.notes_input = ""
    if question is None:
        st.info("全部题目已完成，恭喜！")

question = st.session_state.current_question

if question:
    main_col, side_col = st.columns([2, 1])

    with side_col:
        with st.expander("🔗 相关题目"):
            current_tags = set(question.get("tags", []))
            related = []
            for q in questions:
                if q.get("id") == question.get("id"):
                    continue
                if current_tags.intersection(set(q.get("tags", []))):
                    related.append(q)
            if not related:
                st.caption("暂无相关题目。")
            else:
                for q in related[:8]:
                    label = f"{q.get('id')} - {q.get('title')}"
                    if st.button(label, key=f"rel_{q.get('id')}"):
                        st.session_state.current_question = q
                        st.session_state.code_input = ""
                        st.session_state.notes_input = ""
                        st.rerun()

        with st.expander("📒 查看以往笔记（只读）"):
            history = read_notes(
                question_id=question.get("id"),
                title=question.get("title", ""),
            )
            if history:
                st.text_area("历史笔记", value=history, height=220, disabled=True)
            else:
                st.caption("暂无历史笔记。")

        with st.expander("🤖 AI 思路助手（实验）"):
            ai_cfg = get_ai_config()
            if not ai_cfg["api_key"]:
                st.info("请先设置环境变量 AI_API_KEY 才能调用。")
            prompt = st.text_area("提问", height=120, key="ai_prompt")
            include_context = st.checkbox("附带题目信息", value=True)
            if st.button("发送到 AI"):
                if not ai_cfg["api_key"]:
                    st.error("未配置 AI_API_KEY。")
                elif not prompt.strip():
                    st.warning("请输入问题。")
                else:
                    messages = [{"role": "user", "content": prompt.strip()}]
                    if include_context:
                        context = (
                            f"题目：{question.get('title')}\n"
                            f"难度：{question.get('difficulty')}\n"
                            f"标签：{', '.join(question.get('tags', []))}\n"
                            f"提示：{question.get('pattern_hint')}\n"
                        )
                        messages.insert(
                            0,
                            {
                                "role": "system",
                                "content": "你是算法学习助手，给出思路提示而非完整答案。\n"
                                + context,
                            },
                        )
                    ok, content = call_openai_compatible(
                        messages=messages,
                        model=ai_cfg["model"],
                        base_url=ai_cfg["base_url"],
                        api_key=ai_cfg["api_key"],
                    )
                    if ok:
                        st.write(content)
                    else:
                        st.error(content)

    with main_col:
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
