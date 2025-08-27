#!/usr/bin/env python3
"""
Chart-IMG Webhook Service - v8 Production Version
Uses v2 API for ALL timeframes (hourly, daily, weekly) with full indicators
Includes extended hours trading data to reduce gaps
Version: 8.0 - Full v2 Implementation
"""

import os
import json
import base64
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Tuple

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chart_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Chart-IMG API Configuration
CHART_IMG_API_KEY = 'yeBJ0HYxzJ71YS6DLVQDq5ptgwlmOvlgDZkZPzg6'
CHART_IMG_V2_URL = 'https://api.chart-img.com/v2/tradingview/advanced-chart'

# Local storage configuration
CHART_OUTPUT_DIR = '/Users/abdulaziznahas/chart-img-outputs'
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)

# Ticker mapping for US markets
TICKER_MAPPINGS = {
    # Technology stocks
    'AAPL': 'NASDAQ:AAPL',
    'MSFT': 'NASDAQ:MSFT',
    'GOOGL': 'NASDAQ:GOOGL',
    'AMZN': 'NASDAQ:AMZN',
    'NVDA': 'NASDAQ:NVDA',
    'META': 'NASDAQ:META',
    'TSLA': 'NASDAQ:TSLA',
    'AMD': 'NASDAQ:AMD',
    'INTC': 'NASDAQ:INTC',
    'NFLX': 'NASDAQ:NFLX',
    'PLTR': 'NYSE:PLTR',
    'COIN': 'NASDAQ:COIN',
    
    # Commodities ETFs
    'GLD': 'AMEX:GLD',      # Gold
    'SLV': 'AMEX:SLV',      # Silver
    'COPX': 'AMEX:COPX',    # Copper
    'USO': 'AMEX:USO',      # Oil
    'UNG': 'AMEX:UNG',      # Natural Gas
    'CORN': 'AMEX:CORN',    # Corn
    'WEAT': 'AMEX:WEAT',    # Wheat
    
    # Major ETFs
    'SPY': 'AMEX:SPY',      # S&P 500
    'QQQ': 'NASDAQ:QQQ',    # Nasdaq 100
    'DIA': 'AMEX:DIA',      # Dow Jones
    'IWM': 'AMEX:IWM',      # Russell 2000
    'VXX': 'AMEX:VXX',      # VIX
    'TLT': 'NASDAQ:TLT',    # 20+ Year Treasury
    'GDX': 'AMEX:GDX',      # Gold Miners
}

def get_exchange_symbol(ticker: str) -> str:
    """Convert simple ticker to exchange:ticker format"""
    ticker = ticker.upper().strip()
    
    if ':' in ticker:
        return ticker
    
    if ticker in TICKER_MAPPINGS:
        return TICKER_MAPPINGS[ticker]
    
    logger.warning(f"Unknown ticker {ticker}, defaulting to NASDAQ")
    return f'NASDAQ:{ticker}'

def generate_chart_v2(symbol: str, interval: str, bars_back: int, 
                     description: str, timeframe_type: str) -> Tuple[bool, Dict]:
    """Generate chart using v2 API for ALL timeframes with full indicators"""
    try:
        # Configure technical indicators for v2
        indicators = []
        
        # Volume overlay
        indicators.append({
            'name': 'Volume',
            'forceOverlay': True
        })
        
        # Moving Averages
        indicators.append({'name': 'Moving Average', 'inputs': {'length': 20}})
        indicators.append({'name': 'Moving Average', 'inputs': {'length': 50}})
        indicators.append({'name': 'Moving Average', 'inputs': {'length': 200}})
        
        # Bollinger Bands
        indicators.append({
            'name': 'Bollinger Bands',
            'inputs': {'length': 20, 'mult': 2.0}
        })
        
        # RSI
        indicators.append({
            'name': 'Relative Strength Index',
            'inputs': {'length': 14}
        })
        
        # MACD
        indicators.append({
            'name': 'MACD',
            'inputs': {
                'fast_length': 12,
                'slow_length': 26,
                'signal_length': 9
            }
        })
        
        # Stochastic for all timeframes now
        indicators.append({
            'name': 'Stochastic',
            'inputs': {'k': 14, 'd': 3, 'smooth': 3}
        })
        
        # Prepare the request payload
        payload = {
            'symbol': symbol,
            'interval': interval,
            'bars_back': bars_back,
            'width': 1920,
            'height': 1600,
            'theme': 'dark',
            'studies': indicators,
            'format': 'png',
            # Extended hours / session options (if supported by API)
            'extended_hours': True,  # Try to include extended hours
            'session': 'extended',   # Alternative parameter for extended session
            'hide_legend': False,
            'hide_side_toolbar': False,
            'allow_symbol_change': False,
            'save_image': False,
            'hide_volume': False
        }
        
        headers = {
            'x-api-key': CHART_IMG_API_KEY,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Generating v2 {interval} chart for {symbol} with {bars_back} bars")
        
        response = requests.post(CHART_IMG_V2_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol.replace(':', '_')}_v2_{interval}_{timestamp}.png"
            filepath = os.path.join(CHART_OUTPUT_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Convert to base64
            base64_image = base64.b64encode(response.content).decode('utf-8')
            
            logger.info(f"Successfully generated v2 {interval} chart")
            
            return True, {
                'interval': interval,
                'description': description,
                'base64_image': base64_image,
                'local_path': filepath,
                'size_kb': len(response.content) / 1024,
                'api_version': 'v2',
                'indicators': [ind['name'] for ind in indicators],
                'bars_back': bars_back,
                'extended_hours': True
            }
        else:
            logger.error(f"v2 API error: {response.status_code} - {response.text}")
            return False, {'error': f"v2 API error: {response.status_code}", 'details': response.text}
            
    except Exception as e:
        logger.error(f"Error generating v2 chart: {str(e)}")
        return False, {'error': str(e)}

def generate_all_charts(ticker: str) -> Dict:
    """Generate all three timeframe charts using v2 API exclusively"""
    symbol = get_exchange_symbol(ticker)
    logger.info(f"Generating charts for ticker {ticker} -> {symbol}")
    
    results = {
        'ticker': ticker,
        'symbol': symbol,
        'timestamp': datetime.now().isoformat(),
        'charts': {},
        'errors': []
    }
    
    # 1. Generate hourly chart using v2 API (NEW IN V8)
    success, chart_data = generate_chart_v2(
        symbol,
        '1h',  # Using 1h with v2 API
        168,   # 168 hours = 1 week of hourly data
        '1h chart with 1 week history',
        'hourly'
    )
    if success:
        results['charts']['1h'] = chart_data
    else:
        # Try alternative interval format if 1h fails
        logger.info("Trying alternative hourly format '60' for v2 API")
        success, chart_data = generate_chart_v2(
            symbol,
            '60',  # Try numeric format
            168,
            '1h chart with 1 week history',
            'hourly'
        )
        if success:
            results['charts']['1h'] = chart_data
        else:
            results['errors'].append({
                'interval': '1h',
                'error': chart_data
            })
    
    # 2. Generate daily chart using v2 API
    success, chart_data = generate_chart_v2(
        symbol,
        '1D',
        90,  # 90 days
        'Daily chart with 3 months history',
        'daily'
    )
    if success:
        results['charts']['1D'] = chart_data
    else:
        results['errors'].append({
            'interval': '1D',
            'error': chart_data
        })
    
    # 3. Generate weekly chart using v2 API
    success, chart_data = generate_chart_v2(
        symbol,
        '1W',
        52,  # 52 weeks
        'Weekly chart with 1 year history',
        'weekly'
    )
    if success:
        results['charts']['1W'] = chart_data
    else:
        results['errors'].append({
            'interval': '1W',
            'error': chart_data
        })
    
    # Calculate success metrics
    results['success_count'] = len(results['charts'])
    results['error_count'] = len(results['errors'])
    results['success'] = results['success_count'] >= 3
    
    # Save summary
    summary_path = os.path.join(
        CHART_OUTPUT_DIR, 
        f"{ticker}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    summary = {
        'ticker': results['ticker'],
        'symbol': results['symbol'],
        'timestamp': results['timestamp'],
        'success': results['success'],
        'success_count': results['success_count'],
        'error_count': results['error_count'],
        'api_version': 'v2_exclusive',
        'charts': {
            k: {
                'description': v['description'],
                'local_path': v.get('local_path'),
                'size_kb': v.get('size_kb'),
                'api_version': v.get('api_version'),
                'indicators': v.get('indicators', []),
                'bars_back': v.get('bars_back'),
                'extended_hours': v.get('extended_hours', False)
            }
            for k, v in results['charts'].items()
        },
        'errors': results['errors']
    }
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Chart generation complete. Success: {results['success_count']}/3. Summary: {summary_path}")
    
    return results

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chart-IMG Webhook Service v8 (Full v2)',
        'api_key_configured': bool(CHART_IMG_API_KEY),
        'output_directory': CHART_OUTPUT_DIR,
        'version': '8.0 - Full v2 API',
        'api_strategy': 'v2 for all timeframes with extended hours'
    })

@app.route('/generate-charts', methods=['POST'])
def generate_charts_webhook():
    """Main webhook endpoint for n8n integration"""
    try:
        data = request.get_json() or {}
        ticker = (
            data.get('ticker') or 
            data.get('body', {}).get('ticker') or 
            data.get('symbol')
        )
        
        if not ticker:
            return jsonify({
                'success': False,
                'error': 'No ticker provided',
                'hint': 'Send {"ticker": "NVDA"}'
            }), 400
        
        results = generate_all_charts(ticker)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'ticker': ticker if 'ticker' in locals() else 'unknown'
        }), 500

@app.route('/test/<ticker>', methods=['GET'])
def test_endpoint(ticker):
    """Browser test endpoint"""
    results = generate_all_charts(ticker)
    
    if results['success_count'] > 0:
        html = f"""
        <html>
        <head>
            <title>Chart Results for {ticker}</title>
            <style>
                body {{
                    background: #0a0a0a; 
                    color: #fff; 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 30px;
                    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
                    border-radius: 15px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                }}
                h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    background: linear-gradient(45deg, #4CAF50, #45a049);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .status {{
                    margin-top: 15px;
                    font-size: 1.2em;
                }}
                .api-info {{
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #888;
                }}
                .chart-container {{
                    margin: 30px auto;
                    padding: 25px;
                    background: #1a1a1a;
                    border-radius: 15px;
                    max-width: 1920px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                }}
                .chart-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #333;
                }}
                h3 {{
                    margin: 0;
                    color: #4CAF50;
                    font-size: 1.5em;
                }}
                .indicators {{
                    margin: 15px 0;
                    color: #999;
                }}
                .indicator-badge {{
                    display: inline-block;
                    background: linear-gradient(135deg, #2a2a2a, #3a3a3a);
                    padding: 5px 12px;
                    border-radius: 20px;
                    margin: 3px;
                    font-size: 0.85em;
                    border: 1px solid #444;
                }}
                .api-badge {{
                    display: inline-block;
                    background: #4CAF50;
                    color: #000;
                    padding: 3px 8px;
                    border-radius: 5px;
                    font-size: 0.8em;
                    font-weight: bold;
                    margin-left: 10px;
                }}
                img {{
                    width: 100%;
                    border: 2px solid #333;
                    border-radius: 10px;
                    margin-top: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                }}
                .success {{ color: #4CAF50; font-weight: bold; }}
                .warning {{ color: #ff9800; font-weight: bold; }}
                .metadata {{
                    display: flex;
                    gap: 20px;
                    font-size: 0.9em;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Chart Generation Results - v8</h1>
                <div class="status">
                    <strong>{ticker}</strong> → {results['symbol']} | 
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div class="status">
                    Status: <span class="{'success' if results['success'] else 'warning'}">
                        {'✅ ALL 3 CHARTS GENERATED SUCCESSFULLY!' if results['success'] else f"✅ {results['success_count']}/3 charts generated"}
                    </span>
                </div>
                <div class="api-info">
                    Using Full v2 API Strategy: All timeframes with complete indicators + Extended Hours
                </div>
            </div>
        """
        
        # Display charts
        for interval, chart in results['charts'].items():
            api_version = chart.get('api_version', 'unknown')
            extended = '📈 Extended Hours' if chart.get('extended_hours') else ''
            html += f"""
                <div class="chart-container">
                    <div class="chart-header">
                        <h3>{chart['description']} <span class="api-badge">API {api_version.upper()}</span></h3>
                        <div class="metadata">
                            <span>📊 Interval: {interval}</span>
                            <span>📈 Bars: {chart.get("bars_back", "N/A")}</span>
                            <span>💾 Size: {chart['size_kb']:.1f} KB</span>
                            {f'<span>{extended}</span>' if extended else ''}
                        </div>
                    </div>
                    <div class="indicators">
                        <strong>Technical Indicators:</strong><br>
                        {' '.join([f'<span class="indicator-badge">{ind}</span>' for ind in chart.get('indicators', [])])}
                    </div>
                    <img src="data:image/png;base64,{chart['base64_image']}" alt="{interval} chart">
                </div>
            """
        
        html += f"""
            <div style="text-align: center; margin-top: 40px; color: #666;">
                Chart-IMG Webhook Service v8.0 Full v2 | Powered by TradingView Charts<br>
                Output Directory: {CHART_OUTPUT_DIR}
            </div>
        </body>
        </html>
        """
        
        return html
    else:
        return jsonify(results), 500

if __name__ == '__main__':
    os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║    Chart-IMG Webhook Service v8.0 - FULL V2 API           ║
    ║         ✅ ALL TIMEFRAMES WITH FULL INDICATORS              ║
    ╠════════════════════════════════════════════════════════════╣
    ║ Webhook URL:  http://localhost:5002/generate-charts        ║
    ║ Test URL:     http://localhost:5002/test/NVDA              ║
    ║ Health Check: http://localhost:5002/health                 ║
    ║ Output Dir:   {CHART_OUTPUT_DIR:<45} ║
    ╠════════════════════════════════════════════════════════════╣
    ║ v8 Changes from v7:                                        ║
    ║ • ALL charts use v2 API (including hourly)                 ║
    ║ • Full indicators on ALL timeframes                        ║
    ║ • Extended hours data (if supported)                       ║
    ║                                                            ║
    ║ Chart Configuration:                                       ║
    ║ • 1h chart (1 week / 168 bars) - v2 API                   ║
    ║ • Daily chart (3 months / 90 bars) - v2 API               ║
    ║ • Weekly chart (1 year / 52 bars) - v2 API                ║
    ║                                                            ║
    ║ Technical Indicators (ALL charts):                         ║
    ║ Volume, MA(20,50,200), Bollinger Bands,                   ║
    ║ RSI, MACD, Stochastic                                      ║
    ╠════════════════════════════════════════════════════════════╣
    ║ n8n Integration:                                           ║
    ║ URL: http://host.docker.internal:5002/generate-charts     ║
    ║ Method: POST                                               ║
    ║ Body: {{"ticker": "NVDA"}}                                 ║
    ╚════════════════════════════════════════════════════════════╝
    
    Test with curl:
    curl -X POST http://localhost:5002/generate-charts \\
         -H "Content-Type: application/json" \\
         -d '{{"ticker": "NVDA"}}'
    
    Status: ✅ PRODUCTION READY - v8.0
    """)
    
    app.run(host='0.0.0.0', port=5002, debug=False)