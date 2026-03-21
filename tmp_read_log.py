import os
import re

log_file = "/home/tasubaki/.gemini/antigravity/brain/523de9d2-ef2c-4736-ac97-d3ff8b8bbdfe/.system_generated/logs/overview.txt"
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        # Đọc toàn bộ
        content = f.read()
    
    # Tìm đoạn code C# Sếp gửi trong nội dung chat, thường chứa HtmlAgilityPack
    matches = re.finditer(r".{0,100}HtmlAgilityPack.{0,1000}", content, re.DOTALL | re.IGNORECASE)
    
    count = 0
    for match in matches:
        print("MATCH FOUND:")
        print(match.group(0))
        print("-------------------------------")
        count += 1
        if count >= 3:
            break
            
    if count == 0:
        print("Không tìm thấy HtmlAgilityPack. Thử tìm SelectNode...")
        matches2 = re.finditer(r".{0,300}SelectSingleNode.{0,1000}", content, re.DOTALL | re.IGNORECASE)
        for m in matches2:
            print("MATCH FOUND:")
            print(m.group(0))
            count += 1
            if count >= 3: break
            
else:
    print("Log file not found")
