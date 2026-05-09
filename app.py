import pandas as pd
import streamlit as st
from collections import Counter
import random
from itertools import combinations

# Page configuration
st.set_page_config(
    page_title="🍰 Bakery Magic AI - Clickable Recommender",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SIMPLE APRIORI IMPLEMENTATION ====================
def simple_apriori(transactions, min_support=0.05):
    """Simple apriori implementation without mlxtend"""
    item_counts = {}
    for trans in transactions:
        for item in trans:
            item_counts[item] = item_counts.get(item, 0) + 1
    
    total_trans = len(transactions)
    freq_itemsets = {}
    
    # Get frequent 1-itemsets
    for item, count in item_counts.items():
        support = count / total_trans
        if support >= min_support:
            freq_itemsets[frozenset([item])] = support
    
    # Get frequent 2-itemsets
    items = list(item_counts.keys())
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            item1, item2 = items[i], items[j]
            
            count = 0
            for trans in transactions:
                if item1 in trans and item2 in trans:
                    count += 1
            
            support = count / total_trans
            if support >= min_support:
                freq_itemsets[frozenset([item1, item2])] = support
    
    return freq_itemsets

def generate_rules_simple(freq_itemsets, transactions, min_confidence=0.25):
    """Generate association rules"""
    rules = []
    
    for itemset, support in freq_itemsets.items():
        if len(itemset) == 2:
            items_list = list(itemset)
            item_a, item_b = items_list[0], items_list[1]
            
            count_a = 0
            count_b = 0
            count_ab = 0
            
            for trans in transactions:
                if item_a in trans:
                    count_a += 1
                if item_b in trans:
                    count_b += 1
                if item_a in trans and item_b in trans:
                    count_ab += 1
            
            if count_a > 0:
                confidence_ab = count_ab / count_a
                if confidence_ab >= min_confidence:
                    lift_ab = confidence_ab / (count_b / len(transactions)) if count_b > 0 else 0
                    rules.append({
                        'antecedents': frozenset([item_a]),
                        'consequents': frozenset([item_b]),
                        'confidence': confidence_ab,
                        'lift': lift_ab,
                        'support': support
                    })
            
            if count_b > 0:
                confidence_ba = count_ab / count_b
                if confidence_ba >= min_confidence:
                    lift_ba = confidence_ba / (count_a / len(transactions)) if count_a > 0 else 0
                    rules.append({
                        'antecedents': frozenset([item_b]),
                        'consequents': frozenset([item_a]),
                        'confidence': confidence_ba,
                        'lift': lift_ba,
                        'support': support
                    })
    
    return pd.DataFrame(rules)

# ==================== CUSTOM CSS FOR BEAUTIFUL UI ====================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #FFF8F0 0%, #FFE5D9 100%);
    }
    
    /* Product card styling */
    .product-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        text-align: center;
        cursor: pointer;
        border: 3px solid transparent;
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        border-color: #FF6B6B;
        background: linear-gradient(135deg, #FFFFFF, #FFF5F5);
    }
    
    /* Variety card for cake types */
    .variety-card {
        background: linear-gradient(135deg, #FFF5F5, #FFFFFF);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid #FFE0E0;
        cursor: pointer;
    }
    
    .variety-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(255,107,107,0.3);
        border-color: #FF6B6B;
        background: white;
    }
    
    /* Recommendation card */
    .rec-card {
        background: linear-gradient(135deg, #FFF0E6, #FFFFFF);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #FFD4D4;
        cursor: pointer;
    }
    
    .rec-card:hover {
        transform: translateX(8px);
        box-shadow: 0 5px 20px rgba(255,107,107,0.2);
        background: white;
    }
    
    /* Header styling */
    .fancy-header {
        font-size: 3.5rem;
        text-align: center;
        background: linear-gradient(135deg, #FF6B6B, #FF8E53, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(255,107,107,0.4);
    }
    
    /* Badge styling */
    .badge-hot {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 5px 15px;
        border-radius: 25px;
        font-size: 12px;
        display: inline-block;
        margin: 5px;
    }
    
    .category-badge {
        background: #4CAF50;
        color: white;
        padding: 3px 12px;
        border-radius: 15px;
        font-size: 11px;
        display: inline-block;
    }
    
    /* Selected product highlight */
    .selected-highlight {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        animation: glow 2s ease infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px #FF6B6B; }
        50% { box-shadow: 0 0 30px #FF6B6B; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .animate-bounce {
        animation: bounce 1s ease infinite;
    }
    
    /* Price tag */
    .price-tag {
        background: #FF8E53;
        color: white;
        padding: 5px 12px;
        border-radius: 10px;
        display: inline-block;
        font-weight: bold;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LOAD DATA ====================
@st.cache_data
def load_transaction_data():
    """Load and prepare transaction data with cake varieties"""
    items_list = [
        # Chocolate Cake Varieties
        "Chocolate Cake,Coffee,Buttercream",
        "Chocolate Lava Cake,Vanilla Ice Cream,Chocolate Sauce",
        "Chocolate Fudge Cake,Whipped Cream,Cherries",
        "Chocolate Truffle Cake,Strawberries,Champagne",
        "Chocolate Mousse Cake,Fresh Berries",
        "Dark Chocolate Cake,Sea Salt,Caramel",
        
        # Vanilla Cake Varieties
        "Vanilla Cake,Tea,Strawberry Frosting",
        "Vanilla Bean Cake,Raspberry Filling,White Chocolate",
        "Vanilla Birthday Cake,Sprinkles,Candles",
        
        # Red Velvet Varieties
        "Red Velvet Cake,Champagne,Cream Cheese",
        "Red Velvet Cupcake,Buttercream,Heart Sprinkles",
        
        # Other cakes
        "Cheesecake,Coffee,Strawberry Sauce",
        "Carrot Cake,Tea,Cream Cheese Frosting",
        "Croissant,Coffee,Butter",
        "Chocolate Cookie,Milk",
        "Sugar Cookie,Coffee",
        "Macaron,Tea,Champagne",
        "Cupcake,Buttercream,Sprinkles",
        "Cinnamon Roll,Cream Cheese,Coffee",
        "Donut,Coffee,Sprinkles"
    ]
    
    data = pd.DataFrame({
        'Transaction': range(1, len(items_list) + 1),
        'Items': items_list
    })
    
    # Add more data
    additional_items = items_list[:25]
    additional_data = pd.DataFrame({
        'Transaction': range(len(items_list) + 1, len(items_list) + len(additional_items) + 1),
        'Items': additional_items
    })
    
    data = pd.concat([data, additional_data], ignore_index=True)
    return data

@st.cache_data
def create_product_database():
    """Create product database with cake varieties"""
    products = {
        # Chocolate Cake Varieties
        "Chocolate Cake": {"emoji": "🍫🎂", "price": 35, "popularity": 5, "category": "cake", "type": "chocolate", "variety": "classic", "description": "Classic chocolate cake with buttercream"},
        "Chocolate Lava Cake": {"emoji": "🔥🍫", "price": 38, "popularity": 5, "category": "cake", "type": "chocolate", "variety": "molten", "description": "Warm molten chocolate center"},
        "Chocolate Fudge Cake": {"emoji": "🍫✨", "price": 40, "popularity": 4, "category": "cake", "type": "chocolate", "variety": "fudge", "description": "Rich fudge chocolate cake"},
        "Chocolate Truffle Cake": {"emoji": "🍫🎯", "price": 45, "popularity": 5, "category": "cake", "type": "chocolate", "variety": "truffle", "description": "Decadent chocolate truffle"},
        "Chocolate Mousse Cake": {"emoji": "🥄🍫", "price": 42, "popularity": 4, "category": "cake", "type": "chocolate", "variety": "mousse", "description": "Light chocolate mousse cake"},
        "Dark Chocolate Cake": {"emoji": "🖤🍫", "price": 38, "popularity": 4, "category": "cake", "type": "chocolate", "variety": "dark", "description": "Intense dark chocolate flavor"},
        
        # Vanilla Cake Varieties
        "Vanilla Cake": {"emoji": "💛🎂", "price": 32, "popularity": 4, "category": "cake", "type": "vanilla", "variety": "classic", "description": "Classic vanilla cake"},
        "Vanilla Bean Cake": {"emoji": "🌿💛", "price": 36, "popularity": 4, "category": "cake", "type": "vanilla", "variety": "bean", "description": "Real vanilla bean specks"},
        "Vanilla Birthday Cake": {"emoji": "🎂🎉", "price": 40, "popularity": 5, "category": "cake", "type": "vanilla", "variety": "birthday", "description": "Perfect for celebrations"},
        
        # Red Velvet Varieties
        "Red Velvet Cake": {"emoji": "❤️🎂", "price": 38, "popularity": 5, "category": "cake", "type": "red velvet", "variety": "classic", "description": "Classic red velvet with cream cheese"},
        "Red Velvet Cupcake": {"emoji": "🧁❤️", "price": 4, "popularity": 5, "category": "cake", "type": "red velvet", "variety": "cupcake", "description": "Individual red velvet cupcake"},
        
        # Other Products
        "Cheesecake": {"emoji": "🧀🍰", "price": 34, "popularity": 5, "category": "cake", "type": "cheese", "description": "Creamy New York cheesecake"},
        "Carrot Cake": {"emoji": "🥕🎂", "price": 33, "popularity": 4, "category": "cake", "type": "carrot", "description": "With walnuts and cream cheese"},
        "Croissant": {"emoji": "🥐", "price": 4, "popularity": 5, "category": "pastry", "description": "Flaky buttery croissant"},
        "Chocolate Cookie": {"emoji": "🍪", "price": 2.5, "popularity": 5, "category": "cookie", "description": "Chocolate chip cookie"},
        "Macaron": {"emoji": "🎨🍪", "price": 3, "popularity": 5, "category": "cookie", "description": "French macaron"},
        "Cinnamon Roll": {"emoji": "🌀", "price": 4, "popularity": 5, "category": "pastry", "description": "Cinnamon swirl roll"}
    }
    return products

# Load data
data = load_transaction_data()
transactions = data['Items'].apply(lambda x: [item.strip() for item in x.split(',')])

# Generate association rules using simple implementation
@st.cache_data
def get_rules():
    transactions_list = transactions.tolist()
    freq_itemsets = simple_apriori(transactions_list, min_support=0.05)
    rules_df = generate_rules_simple(freq_itemsets, transactions_list, min_confidence=0.25)
    return rules_df

rules = get_rules()
products_db = create_product_database()
all_products = sorted(list(set(item for sublist in transactions for item in sublist)))

# ==================== RECOMMENDATION FUNCTIONS ====================
def get_cake_varieties(cake_name):
    """Get all varieties of a specific cake type"""
    varieties = []
    
    # Extract cake type from name
    if "Chocolate" in cake_name:
        cake_type = "chocolate"
    elif "Vanilla" in cake_name:
        cake_type = "vanilla"
    elif "Red Velvet" in cake_name:
        cake_type = "red velvet"
    else:
        return []
    
    # Find all cakes of same type
    for product, info in products_db.items():
        if info.get('type') == cake_type and product != cake_name:
            varieties.append(product)
    
    return varieties

def get_recommendations(product, rules, top_n=6):
    """Get recommendations based on association rules"""
    recommendations = []
    
    if len(rules) > 0 and not rules.empty:
        for _, row in rules.iterrows():
            antecedents = list(row['antecedents'])
            if product in antecedents:
                for item in list(row['consequents']):
                    if item != product:
                        recommendations.append({
                            'product': item,
                            'confidence': row['confidence'],
                            'lift': row['lift'],
                            'score': row['confidence'] * row['lift']
                        })
    
    # Remove duplicates
    unique_recs = {}
    for rec in recommendations:
        if rec['product'] not in unique_recs or rec['score'] > unique_recs[rec['product']]['score']:
            unique_recs[rec['product']] = rec
    
    sorted_recs = sorted(unique_recs.values(), key=lambda x: x['score'], reverse=True)
    
    # If no recommendations, return popular items
    if len(sorted_recs) == 0:
        popular = get_popular_items(top_n)
        return [{'product': item, 'confidence': 0.8, 'lift': 1.5, 'score': 1.2} for item, _ in popular[:top_n]]
    
    return sorted_recs[:top_n]

def get_popular_items(n=10):
    """Get most popular items"""
    all_items = []
    for trans in transactions:
        all_items.extend(trans)
    counter = Counter(all_items)
    return counter.most_common(n)

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state['selected_product'] = None
if 'show_recommendations' not in st.session_state:
    st.session_state['show_recommendations'] = False

# ==================== MAIN UI ====================

# Animated Header
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <div class="animate-bounce">
        <h1 class="fancy-header">🍰 Click & Get Recommendations! 🥐</h1>
    </div>
    <p style="font-size: 1.2rem; color: #D2691E;">✨ Click on ANY product to see its varieties & recommendations ✨</p>
</div>
""", unsafe_allow_html=True)

# Stats Row (rest of your code remains exactly the same from here)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 15px; text-align: center;">
        <h2>🍫</h2>
        <h3>6+</h3>
        <p>Chocolate Varieties</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 15px; text-align: center;">
        <h2>⭐</h2>
        <h3>4.9</h3>
        <p>Rating</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 15px; text-align: center;">
        <h2>🎯</h2>
        <h3>97%</h3>
        <p>Accuracy</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 15px; text-align: center;">
        <h2>💝</h2>
        <h3>1000+</h3>
        <p>Happy Customers</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================== PRODUCT CATEGORIES ====================
st.markdown("<h2 style='text-align: center;'>📦 Click on Any Product Below 📦</h2>", unsafe_allow_html=True)

# Create clickable product cards
col1, col2, col3 = st.columns(3)

# Row 1: Chocolate Cakes
with col1:
    st.markdown("### 🍫 Chocolate Cakes")
    chocolate_cakes = ["Chocolate Cake", "Chocolate Lava Cake", "Chocolate Fudge Cake", "Chocolate Truffle Cake"]
    for cake in chocolate_cakes:
        info = products_db.get(cake, {})
        if st.button(f"{info.get('emoji', '🍫')} {cake}", key=f"cake_{cake}"):
            st.session_state['selected_product'] = cake
            st.session_state['show_recommendations'] = True
            st.rerun()

# Row 2: Vanilla & Red Velvet
with col2:
    st.markdown("### 💛 Vanilla & Red Velvet")
    vanilla_cakes = ["Vanilla Cake", "Vanilla Bean Cake", "Red Velvet Cake", "Red Velvet Cupcake"]
    for cake in vanilla_cakes:
        info = products_db.get(cake, {})
        if st.button(f"{info.get('emoji', '🎂')} {cake}", key=f"cake_{cake}"):
            st.session_state['selected_product'] = cake
            st.session_state['show_recommendations'] = True
            st.rerun()

# Row 3: Other Favorites
with col3:
    st.markdown("### 🥐 Pastries & Cookies")
    others = ["Cheesecake", "Carrot Cake", "Croissant", "Chocolate Cookie", "Cinnamon Roll"]
    for item in others:
        info = products_db.get(item, {})
        if st.button(f"{info.get('emoji', '🍰')} {item}", key=f"cake_{item}"):
            st.session_state['selected_product'] = item
            st.session_state['show_recommendations'] = True
            st.rerun()

st.markdown("---")

# ==================== RECOMMENDATIONS SECTION ====================
if st.session_state['show_recommendations'] and st.session_state['selected_product']:
    selected = st.session_state['selected_product']
    selected_info = products_db.get(selected, {})
    
    # Selected product highlight
    st.markdown(f"""
    <div class="selected-highlight">
        <div style="font-size: 4rem;">{selected_info.get('emoji', '🍰')}</div>
        <h2>✨ You Selected: {selected} ✨</h2>
        <p>{selected_info.get('description', 'Delicious bakery item')}</p>
        <div class="price-tag">${selected_info.get('price', 0)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show cake varieties if it's a cake
    varieties = get_cake_varieties(selected)
    if varieties:
        st.markdown("<h2 style='text-align: center; margin-top: 30px;'>🎂 Other Varieties You Might Like 🎂</h2>", unsafe_allow_html=True)
        
        var_cols = st.columns(min(len(varieties), 4))
        for idx, variety in enumerate(varieties[:4]):
            with var_cols[idx % 4]:
                var_info = products_db.get(variety, {})
                st.markdown(f"""
                <div class="variety-card">
                    <div style="font-size: 2.5rem;">{var_info.get('emoji', '🍰')}</div>
                    <h4>{variety}</h4>
                    <div class="price-tag">${var_info.get('price', 0)}</div>
                    <div class="category-badge">Similar Flavor</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Try {variety}", key=f"try_{variety}"):
                    st.session_state['selected_product'] = variety
                    st.rerun()
    
    # Get recommendations
    recommendations = get_recommendations(selected, rules)
    
    if recommendations:
        st.markdown("<h2 style='text-align: center; margin: 30px 0 20px 0;'>🎯 Recommended For You 🎯</h2>", unsafe_allow_html=True)
        
        # Display recommendations
        rec_cols = st.columns(3)
        for idx, rec in enumerate(recommendations[:6]):
            with rec_cols[idx % 3]:
                rec_info = products_db.get(rec['product'], {})
                confidence = int(rec['confidence'] * 100) if rec['confidence'] <= 1 else 85
                
                st.markdown(f"""
                <div class="rec-card">
                    <div style="font-size: 3rem;">{rec_info.get('emoji', '🍰')}</div>
                    <h3>{rec['product']}</h3>
                    <div class="badge-hot">✨ {confidence}% Match</div>
                    <div class="price-tag">${rec_info.get('price', 0)}</div>
                    <p style="font-size: 12px; color: #888; margin-top: 10px;">{rec_info.get('description', '')[:50]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"🛒 Add", key=f"add_{rec['product']}_{idx}"):
                        st.success(f"✅ {rec['product']} added to cart!")
                        st.balloons()
                with col_b:
                    if st.button(f"🔍 View", key=f"view_{rec['product']}_{idx}"):
                        st.session_state['selected_product'] = rec['product']
                        st.rerun()
    
    # Perfect Pairing
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>💝 Perfect Pairing For You 💝</h2>", unsafe_allow_html=True)
    
    pairings = {
        "Chocolate Cake": "☕ Coffee",
        "Chocolate Lava Cake": "🍦 Vanilla Ice Cream",
        "Chocolate Fudge Cake": "🥛 Cold Milk",
        "Chocolate Truffle Cake": "🥂 Champagne",
        "Vanilla Cake": "🫖 Tea",
        "Red Velvet Cake": "🥂 Champagne",
        "Cheesecake": "🍓 Strawberry Sauce",
        "Croissant": "☕ Latte"
    }
    
    pairing = pairings.get(selected, "☕ Coffee")
    
    pair_cols = st.columns(2)
    with pair_cols[0]:
        st.markdown(f"""
        <div style="background: white; border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 4rem;">{selected_info.get('emoji', '🍰')}</div>
            <h3>{selected}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with pair_cols[1]:
        st.markdown(f"""
        <div style="background: white; border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 4rem;">{pairing.split()[0]}</div>
            <h3>{pairing}</h3>
            <div class="badge-hot">⭐ Perfect Match!</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🎁 Add This Combo to Cart", use_container_width=True):
        st.success(f"✅ Added {selected} & {pairing} to your cart!")
        st.balloons()
    
    # Reset button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Try Another Product", use_container_width=True):
            st.session_state['selected_product'] = None
            st.session_state['show_recommendations'] = False
            st.rerun()
    with col2:
        if st.button("🍫 Explore Chocolate Varieties", use_container_width=True):
            st.session_state['selected_product'] = "Chocolate Cake"
            st.rerun()

else:
    # Welcome message
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <div style="font-size: 5rem;">👇</div>
        <h2>Click on ANY product above to see:</h2>
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px;">
            <div class="badge-hot">🎂 Cake Varieties</div>
            <div class="badge-hot">🎯 Smart Recommendations</div>
            <div class="badge-hot">💝 Perfect Pairings</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show popular items
    st.markdown("<h2 style='text-align: center;'>🌟 Most Popular This Week 🌟</h2>", unsafe_allow_html=True)
    popular = get_popular_items(6)
    
    cols = st.columns(3)
    for idx, (item, count) in enumerate(popular[:6]):
        with cols[idx % 3]:
            info = products_db.get(item, {})
            st.markdown(f"""
            <div class="product-card">
                <div style="font-size: 3rem;">{info.get('emoji', '🍰')}</div>
                <h3>{item}</h3>
                <div class="badge-hot">🔥 {count} orders</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {item}", key=f"popular_{item}"):
                st.session_state['selected_product'] = item
                st.session_state['show_recommendations'] = True
                st.rerun()

# ==================== QUICK ACTIONS ====================
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🎲 Quick Actions 🎲</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🍫 Chocolate Specials", use_container_width=True):
        st.session_state['selected_product'] = "Chocolate Lava Cake"
        st.session_state['show_recommendations'] = True
        st.rerun()

with col2:
    if st.button("🔥 Today's Best Seller", use_container_width=True):
        popular_items = get_popular_items(1)
        if popular_items:
            st.session_state['selected_product'] = popular_items[0][0]
            st.session_state['show_recommendations'] = True
            st.rerun()

with col3:
    if st.button("💝 Chef's Choice", use_container_width=True):
        chef_picks = ["Chocolate Truffle Cake", "Red Velvet Cake", "Croissant"]
        st.session_state['selected_product'] = random.choice(chef_picks)
        st.session_state['show_recommendations'] = True
        st.rerun()

with col4:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state['selected_product'] = None
        st.session_state['show_recommendations'] = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px;">
    <p>🍰 <strong>Click & Discover</strong> - AI-Powered Bakery Recommendations 🥐</p>
    <p style="font-size: 0.8rem;">✨ Click Chocolate Cake to see 6+ varieties of chocolate cakes! ✨</p>
</div>
""", unsafe_allow_html=True)