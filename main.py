import streamlit as st
import hashlib
import datetime as dt

# =========================
# Full-width page config
# =========================
st.set_page_config(
    page_title="Simple Blockchain Demo",
    layout="wide",
    initial_sidebar_state="auto"
)

# =========================
# CSS Styling
# =========================
st.markdown(
    """
    <style>
    /* Body background */
    .reportview-container {
        background-color: #f5f7fa;
    }
    /* Title style */
    h1 {
        text-align: center;
        color: #0a9396;
    }
    /* Subheaders */
    h3 {
        color: #005f73;
    }
    /* Expander block styling */
    .stExpander {
        background-color: #e0fbfc;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* Buttons */
    div.stButton > button:first-child {
        background-color: #0a9396;
        color: white;
        height: 40px;
        width: 100%;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        margin-bottom: 5px;
    }
    /* Input boxes */
    .stTextInput > div > input {
        border-radius: 10px;
        border: 1px solid #94d2bd;
        padding: 5px;
    }
    /* Selectbox */
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 1px solid #94d2bd;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True
)

# =========================
# BLOCK CLASS
# =========================
class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return hashlib.sha256(block_string.encode()).hexdigest()


# =========================
# BLOCKCHAIN CLASS
# =========================
class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.difficulty = difficulty

    def create_genesis_block(self):
        genesis = Block(0, str(dt.datetime.now()), "Genesis Block", "0")
        self.chain.append(genesis)
        return genesis

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def mine_block(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr.hash != curr.calculate_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
        return True

# =======================================================
# STREAMLIT WEB APPLICATION
# =======================================================
st.markdown("<h1>Simple Blockchain Demo</h1>", unsafe_allow_html=True)

# Initialize blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = None

blockchain = st.session_state.blockchain

# Layout: two columns
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("<h3>🚀 Node Blockchain</h3>", unsafe_allow_html=True)
    if blockchain is None:
        if st.button("Tạo Node Blockchain"):
            st.session_state.blockchain = Blockchain(difficulty=4)
            blockchain = st.session_state.blockchain
            genesis_block = blockchain.create_genesis_block()
            st.success(f"Block Genesis đã được tạo! Hash: {genesis_block.hash}")
    else:
        st.success("Node Blockchain đã được tạo!")

    if blockchain:
        st.markdown("<h3>➕ Thêm Block mới</h3>", unsafe_allow_html=True)
        user_data = st.text_input("Nhập dữ liệu cho Block:", key="add_block")
        if st.button("Mine và thêm Block"):
            if user_data == "":
                st.warning("Phải nhập dữ liệu.")
            else:
                new_block = Block(
                    index=len(blockchain.chain),
                    timestamp=str(dt.datetime.now()),
                    data=user_data,
                    previous_hash=blockchain.get_latest_block().hash
                )
                with st.spinner("⛏️ Đang đào ..."):
                    mined_block = blockchain.mine_block(new_block)
                blockchain.add_block(mined_block)
                st.success(f"Block #{mined_block.index} đào thành công!")
                st.write("Hash:", mined_block.hash)

        st.markdown("<h3>🔍 Xác thực Blockchain</h3>", unsafe_allow_html=True)
        if st.button("Kiểm tra tính toàn vẹn của Blockchain"):
            if blockchain.is_chain_valid():
                st.success("✅ Blockchain hợp lệ!")
            else:
                st.error("❌ Blockchain không hợp lệ!")

        st.markdown("<h3>⚠️ Thay đổi dữ liệu một Block</h3>", unsafe_allow_html=True)
        if len(blockchain.chain) > 1:
            block_indices = [str(b.index) for b in blockchain.chain[1:]]
            selected_index = st.selectbox("Chọn block để thay đổi:", block_indices, key="tamper_index")
            tamper_data = st.text_input("Nhập dữ liệu mới:", key="tamper_data")
            if st.button("Thay đổi dữ liệu"):
                if tamper_data == "":
                    st.warning("Nhập dữ liệu mới để thay đổi block")
                else:
                    idx = int(selected_index)
                    block_to_tamper = blockchain.chain[idx]
                    old_data = block_to_tamper.data
                    block_to_tamper.data = tamper_data
                    block_to_tamper.hash = block_to_tamper.calculate_hash()
                    st.error(f"Block #{idx} đã thay đổi dữ liệu từ '{old_data}' sang '{tamper_data}'!")

with col_right:
    st.markdown("<h3>📜 Sổ cái Blockchain</h3>", unsafe_allow_html=True)
    if blockchain:
        with st.container():
            for block in blockchain.chain:
                with st.expander(f"Block #{block.index}"):
                    st.write("**Timestamp:**", block.timestamp)
                    st.write("**Data:**", block.data)
                    st.write("**Nonce:**", block.nonce)
                    st.write("**Previous Hash:**", block.previous_hash)
                    st.write("**Hash:**", block.hash)
    else:
        st.info("Chưa có Node Blockchain. Vui lòng tạo Node bên trái.")
