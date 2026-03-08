from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8515")
    page.wait_for_timeout(2000)
    
    # Fill in login
    page.fill("input[type='text']", "admin")
    page.fill("input[type='password']", "admin@123")
    
    # Click Sign In (button containing 'Sign In')
    page.click("button:has-text('Sign In')")
    
    page.wait_for_timeout(3000)
    
    # Look for error boxes
    error_elements = page.locator(".stException").all()
    if error_elements:
        print("FOUND ERROR TRACEBACK(S):")
        for err in error_elements:
            print(err.inner_text())
    else:
        print("No Streamlit exceptions found on page.")
        
    browser.close()
