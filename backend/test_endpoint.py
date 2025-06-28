#!/usr/bin/env python3
"""
Test script to reproduce the exact frontend API call
"""
import requests

def test_textual_analysis():
    """Test the textual analysis endpoint with the same data as frontend"""
    
    # Exact same URL as frontend
    url = "http://localhost:8000/patient/textual_analysis"
    
    # Create form data exactly like frontend
    form_data = {
        'user_symptoms': 'I have a headache and feel dizzy',
        'session_id': 'session_test_123'
    }
    
    print(f"🔍 Testing URL: {url}")
    print(f"🔍 Form data: {form_data}")
    
    try:
        response = requests.post(url, data=form_data)
        
        print(f"🔍 Status Code: {response.status_code}")
        print(f"🔍 Status Text: {response.reason}")
        print(f"🔍 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            print(f"✅ Response: {result}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"❌ Error Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_textual_analysis()
