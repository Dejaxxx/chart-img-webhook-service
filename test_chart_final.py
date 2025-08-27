#!/usr/bin/env python3
"""
Final Test for Chart-IMG Service v7 Hybrid
Tests multiple tickers to ensure all 3 charts generate successfully
"""

import requests
import json
import time
import sys

def test_chart_service():
    """Comprehensive test of the Chart-IMG service"""
    
    print("🎯 Chart-IMG Service v7 Hybrid - Final Test")
    print("=" * 60)
    
    # Check if service is running
    try:
        health = requests.get('http://localhost:5002/health')
        if health.status_code == 200:
            health_data = health.json()
            print("✅ Service is healthy")
            print(f"   Version: {health_data['version']}")
            print(f"   API Strategy: {health_data['api_strategy']}")
        else:
            print("❌ Service health check failed")
            return False
    except:
        print("❌ Service not running. Start with: ./start_chart_service.sh")
        return False
    
    # Test multiple tickers
    test_cases = [
        ('NVDA', 'Tech Stock'),
        ('GLD', 'Gold ETF'),
        ('SPY', 'S&P 500 ETF'),
        ('AAPL', 'Apple Stock'),
        ('TSLA', 'Tesla Stock')
    ]
    
    all_success = True
    results_summary = []
    
    for ticker, description in test_cases:
        print(f"\n📊 Testing {ticker} ({description})...")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:5002/generate-charts',
                json={'ticker': ticker},
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Detailed results
                print(f"Symbol: {data['symbol']}")
                print(f"Success: {'✅ YES' if data['success'] else '⚠️  PARTIAL'}")
                print(f"Charts Generated: {data['success_count']}/3")
                print(f"Time: {elapsed:.1f} seconds")
                
                # Show each chart
                if data.get('charts'):
                    print("\nCharts Generated:")
                    for interval, chart in data['charts'].items():
                        api_version = chart.get('api_version', 'unknown')
                        size_kb = chart.get('size_kb', 0)
                        indicators = len(chart.get('indicators', []))
                        print(f"  ✓ {interval} - {chart['description']} (API {api_version})")
                        print(f"    Size: {size_kb:.1f} KB, Indicators: {indicators}")
                
                # Track results
                results_summary.append({
                    'ticker': ticker,
                    'success': data['success'],
                    'count': data['success_count'],
                    'time': elapsed
                })
                
                if data['success_count'] < 3:
                    all_success = False
                    print(f"\n⚠️  Warning: Only {data['success_count']}/3 charts generated")
                    if data.get('errors'):
                        for error in data['errors']:
                            print(f"   Error: {error}")
                            
            else:
                print(f"❌ Request failed: {response.status_code}")
                all_success = False
                results_summary.append({
                    'ticker': ticker,
                    'success': False,
                    'count': 0,
                    'time': elapsed
                })
                
        except Exception as e:
            print(f"❌ Error testing {ticker}: {str(e)}")
            all_success = False
            results_summary.append({
                'ticker': ticker,
                'success': False,
                'count': 0,
                'time': 0
            })
        
        # Small delay between requests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 FINAL TEST SUMMARY")
    print("=" * 60)
    
    total_charts = sum(r['count'] for r in results_summary)
    total_possible = len(test_cases) * 3
    avg_time = sum(r['time'] for r in results_summary if r['time'] > 0) / len([r for r in results_summary if r['time'] > 0])
    
    print(f"\nTickers Tested: {len(test_cases)}")
    print(f"Total Charts Generated: {total_charts}/{total_possible}")
    print(f"Success Rate: {(total_charts/total_possible)*100:.1f}%")
    print(f"Average Time: {avg_time:.1f} seconds")
    
    print("\nPer Ticker Results:")
    for result in results_summary:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['ticker']}: {result['count']}/3 charts ({result['time']:.1f}s)")
    
    if all_success and total_charts == total_possible:
        print("\n🎉 ALL TESTS PASSED! Service is working perfectly!")
        print("   All 3 charts generated for all tickers")
        return True
    else:
        print("\n⚠️  Some issues detected, but service is operational")
        return False
    
    print(f"\n💡 View charts in browser:")
    print("   http://localhost:5002/test/NVDA")
    print("   http://localhost:5002/test/GLD")
    print("   http://localhost:5002/test/SPY")

if __name__ == "__main__":
    success = test_chart_service()
    sys.exit(0 if success else 1)
