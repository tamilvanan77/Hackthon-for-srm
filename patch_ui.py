import re
import os

file_path = r"d:\website\Student warning\app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace primary blue color #4F8BF9 and #38bdf8 with a vibrant purple-pink Luxe gradient
content = content.replace("linear-gradient(135deg, #4F8BF9 0%, #38bdf8 100%)", "linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)")
content = content.replace("linear-gradient(135deg, #ffffff 0%, #38bdf8 60%, #818cf8 100%)", "linear-gradient(135deg, #ffffff 0%, #d946ef 60%, #8b5cf6 100%)")
content = content.replace("linear-gradient(135deg, #4F8BF9 0%, #38bdf8 50%, #818cf8 100%)", "linear-gradient(135deg, #8b5cf6 0%, #d946ef 50%, #f43f5e 100%)")
content = content.replace("linear-gradient(135deg, #60a5fa 0%, #38bdf8 100%)", "linear-gradient(135deg, #c084fc 0%, #f472b6 100%)")

# Update box shadows and borders from blue to purple/fuchsia
content = content.replace("rgba(79, 139, 249,", "rgba(217, 70, 239,")
content = content.replace("rgba(56, 189, 248,", "rgba(139, 92, 246,")
content = content.replace("#4F8BF9", "#d946ef")
content = content.replace("#38bdf8", "#8b5cf6")
content = content.replace("#60a5fa", "#c084fc")
content = content.replace("#818cf8", "#f472b6")

# Enhance Animations
# 1. kpi-card hover
content = content.replace("transform: translateY(-4px);", "transform: translateY(-6px) scale(1.02);")
# 2. Add floating animation to KPI Card icons
content = content.replace('<div style="font-size: 1.5rem;">{icon}</div>', '<div style="font-size: 1.8rem; animation: float 3s ease-in-out infinite;">{icon}</div>')
# 3. Enhance pulse-red
old_pulse = '''    @keyframes pulse-red {
        0%   { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70%  { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }'''
new_pulse = '''    @keyframes pulse-red {
        0%   { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); transform: scale(1); }
        50%  { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); transform: scale(1.05); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); transform: scale(1); }
    }'''
content = content.replace(old_pulse, new_pulse)

# 4. Enhance float
old_float = '''    @keyframes float {
        0%   { transform: translateY(0px); }
        50%  { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }'''
new_float = '''    @keyframes float {
        0%   { transform: translateY(0px) rotate(0deg); }
        50%  { transform: translateY(-6px) rotate(4deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }'''
content = content.replace(old_float, new_float)

content = content.replace("    @keyframes float", "    @keyframes gradient-shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }\\n    @keyframes float")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("CSS colors and animations updated.")
