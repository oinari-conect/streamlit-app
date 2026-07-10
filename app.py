import streamlit as st
import json
import os
import shutil
import logging
from datetime import datetime

# 定数
TODOS_FILE = "todos.json"
BACKUP_DIR = ".backups"

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_backup_dir():
    """バックアップディレクトリを確保"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup():
    """JSON ファイルのバックアップを作成"""
    if os.path.exists(TODOS_FILE):
        try:
            ensure_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"todos_backup_{timestamp}.json")
            shutil.copy2(TODOS_FILE, backup_file)
            logger.info(f"Backup created: {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

# JSON ファイルからタスクを読み込む関数
def load_todos():
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            create_backup()
            return []
        except (IOError, OSError) as e:
            logger.error(f"File operation error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading todos: {e}")
            return []
    return []

# タスクを JSON ファイルに保存する関数
def save_todos(todos):
    try:
        # 保存前にバックアップを作成
        create_backup()
        
        with open(TODOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        logger.info(f"Todos saved successfully: {len(todos)} tasks")
    except (IOError, OSError) as e:
        logger.error(f"File operation error while saving: {e}")
        st.error(f"ファイル保存エラー: {e}")
    except Exception as e:
        logger.error(f"Unexpected error saving todos: {e}")
        st.error(f"予期しないエラーが発生しました: {e}")

def get_last_modified_time():
    """最終更新時刻を取得"""
    if os.path.exists(TODOS_FILE):
        try:
            timestamp = os.path.getmtime(TODOS_FILE)
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "不明"
    return "未保存"

# セッション状態の初期化
if 'todos' not in st.session_state:
    st.session_state.todos = load_todos()

# 次のタスク ID を生成する関数
def get_next_id():
    if not st.session_state.todos:
        return 1
    return max(todo['id'] for todo in st.session_state.todos) + 1

st.title("TODOアプリ")

# 最終更新時刻を表示
last_modified = get_last_modified_time()
st.caption(f"📅 最終更新: {last_modified}")

# タスク入力とボタン
col1, col2 = st.columns([4, 1])
with col1:
    task_input = st.text_input("タスク入力", key="task_input")
with col2:
    if st.button("追加"):
        if task_input.strip():
            new_todo = {
                "id": get_next_id(),
                "text": task_input,
                "done": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            st.session_state.todos.append(new_todo)
            save_todos(st.session_state.todos)
            st.session_state.task_input = ""
            st.rerun()

# フィルター機能
if st.session_state.todos:
    st.subheader("フィルター")
    filter_option = st.radio("表示するタスク:", ("すべて", "未完了", "完了"), horizontal=True)
    
    # フィルター適用
    if filter_option == "すべて":
        filtered_todos = st.session_state.todos
    elif filter_option == "未完了":
        filtered_todos = [todo for todo in st.session_state.todos if not todo["done"]]
    else:  # 完了
        filtered_todos = [todo for todo in st.session_state.todos if todo["done"]]
    
    # タスク一覧表示
    st.subheader("タスク一覧")
    
    for i, todo in enumerate(filtered_todos):
        col_checkbox, col_text, col_delete = st.columns([1, 4, 1])
        
        with col_checkbox:
            # チェックボックス
            new_done_state = st.checkbox(
                "完了",
                value=todo["done"],
                key=f"checkbox_{todo['id']}"
            )
            
            # ステータス変更検知
            if new_done_state != todo["done"]:
                for t in st.session_state.todos:
                    if t["id"] == todo["id"]:
                        t["done"] = new_done_state
                        t["updated_at"] = datetime.now().isoformat()
                        break
                save_todos(st.session_state.todos)
                st.rerun()
        
        with col_text:
            # テキスト表示（完了時は打ち消し線）
            if todo["done"]:
                st.write(f"~~{todo['text']}~~")
            else:
                st.write(todo["text"])
        
        with col_delete:
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{todo['id']}"):
                st.session_state.todos = [
                    t for t in st.session_state.todos if t["id"] != todo["id"]
                ]
                save_todos(st.session_state.todos)
                st.rerun()
else:
    st.info("タスクがまだ登録されていません")
