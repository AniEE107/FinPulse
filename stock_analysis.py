import streamlit as st
import yfinance as yf
from langchain_community.llms import Ollama
from langchain.tools import tool
from langchain.agents import AgentType, initialize_agent
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import tweepy

# Initialize Ollama
llm = Ollama(model="mistral")

# Twitter API Configuration
CONSUMER_KEY = "Qc0otlOyG2hg7Iq2gcCDkK9Dz"
CONSUMER_SECRET = "qEpwI5NexR3lNbqfwiOj9I7voOlQSAl7zn7qDq6o6Dp4ppiph4"
ACCESS_TOKEN = "1940249969971380224-YnImIBmD70AZ7lINN1Y0DNC9Nxrg7Z"
ACCESS_TOKEN_SECRET = "i9pDeh8gXMEVhsLHLLqrstUnbKaJKSn3lx65r8Mc3QaLr"

@tool
def fetch_tweets(query: str) -> str:
    """Fetch recent tweets for the given stock symbol using Tweepy."""
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        tweets = []
        # Search for tweets containing the stock symbol (with $ prefix)
        for tweet in tweepy.Cursor(api.search_tweets, 
                                 q=f"${query} -filter:retweets",
                                 lang="en",
                                 tweet_mode='extended',
                                 result_type="recent").items(10):
            tweets.append(f"{tweet.created_at}: {tweet.full_text}")
        
        return "\n".join(tweets) if tweets else f"No recent tweets found about ${query}"
    except tweepy.TweepyException as e:
        return f"Twitter API error: {str(e)}"
    except Exception as e:
        return f"Error fetching tweets: {str(e)}"

@tool
def fetch_stock_price(symbol: str) -> str:
    """Fetch comprehensive stock data for the given symbol."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")
        if hist.empty:
            return f"No data found for {symbol}"
            
        latest = hist.iloc[-1]
        price_change = latest['Close'] - hist.iloc[0]['Close']
        percent_change = (price_change / hist.iloc[0]['Close']) * 100
        
        # Get additional info
        info = stock.info
        company_name = info.get('shortName', symbol)
        pe_ratio = info.get('trailingPE', 'N/A')
        
        trend = "↑ Upward" if percent_change > 0 else "↓ Downward"
        return (
            f"Company: {company_name}\n"
            f"Symbol: {symbol}\n"
            f"Current Price: ${latest['Close']:.2f}\n"
            f"1M Change: ${price_change:.2f} ({percent_change:.2f}%)\n"
            f"Trend: {trend}\n"
            f"PE Ratio: {pe_ratio}\n"
            f"Volume: {latest['Volume']:,}"
        )
    except Exception as e:
        return f"Error fetching stock data: {str(e)}"

# Initialize agent with enhanced configuration
tools = [fetch_tweets, fetch_stock_price]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# LangGraph setup
class AgentState(dict): pass

def agent_node(state: dict) -> dict:
    query = state.get("question")
    if not query:
        return {"error": "Missing 'question' in state."}
        
    try:
        response = agent.invoke(query)
        return {"question": query, "response": response}
    except Exception as e:
        return {"error": f"Agent error: {str(e)}"}

workflow = StateGraph(dict)
workflow.add_node("agent_node", RunnableLambda(agent_node))
workflow.set_entry_point("agent_node")
workflow.set_finish_point("agent_node")
executable_graph = workflow.compile()

# Enhanced Streamlit UI
def main():
    st.set_page_config(
        page_title="Stock Analysis Assistant", 
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Stock Analysis Assistant")
    st.markdown("""
    **AI-powered investment analysis** combining real-time Twitter sentiment and stock market data.
    """)
    
    with st.expander("ℹ️ How to use", expanded=True):
        st.write("""
        1. Enter a stock symbol (e.g., TSLA, AAPL)
        2. Select your question type
        3. Click 'Analyze' to get an AI-powered recommendation
        """)
    
    # Input Section
    col1, col2 = st.columns([1, 2])
    with col1:
        stock_symbol = st.text_input(
            "Stock Symbol", 
            "TSLA",
            placeholder="e.g., TSLA, AAPL",
            help="Enter the stock ticker symbol"
        ).strip().upper()
        
    with col2:
        query_type = st.selectbox(
            "Analysis Type",
            [
                "Should I buy this stock?",
                "What's the current sentiment for this stock?",
                "Technical analysis of this stock",
                "Custom question"
            ],
            index=0,
            help="Select the type of analysis you want"
        )
        
        if query_type == "Custom question":
            user_question = st.text_input(
                "Your Question",
                placeholder="Ask any question about this stock..."
            )
        else:
            user_question = query_type.replace("this", stock_symbol)
    
    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        if not stock_symbol:
            st.error("Please enter a valid stock symbol")
            st.stop()
            
        with st.spinner("🧠 Analyzing data and generating insights..."):
            try:
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Stock Data", "🐦 Twitter Sentiment", "🤖 AI Analysis"])
                
                with tab1:
                    stock_data = fetch_stock_price(stock_symbol)
                    st.subheader(f"Stock Data for {stock_symbol}")
                    st.text_area(
                        "Stock Information", 
                        stock_data, 
                        height=200,
                        label_visibility="collapsed"
                    )
                
                with tab2:
                    tweets = fetch_tweets(stock_symbol)
                    st.subheader(f"Recent Tweets about {stock_symbol}")
                    st.text_area(
                        "Twitter Data", 
                        tweets, 
                        height=200,
                        label_visibility="collapsed"
                    )
                
                with tab3:
                    result = executable_graph.invoke({"question": user_question})
                    
                    if result and isinstance(result, dict):
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            response = result.get("response", {})
                            analysis = response.get("output", str(response))
                            
                            st.success("Analysis Complete!")
                            st.subheader("AI Recommendation")
                            st.markdown("---")
                            st.write(analysis)
                            st.markdown("---")
                            st.caption("Note: This is AI-generated advice. Please consult a financial advisor before making investment decisions.")
                    else:
                        st.error("No response from analysis agent.")
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")

if __name__ == "__main__":
    main()
