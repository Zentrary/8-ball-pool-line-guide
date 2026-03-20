# 🎱 8 Ball Pool Guideline Overlay v2

![Preview](Images/Images.png)

โปรแกรม **Guideline Overlay สำหรับเกม 8 Ball Pool** ช่วยแสดงเส้นแนวการยิงจากตำแหน่งลูกขาวไปยังหลุมต่าง ๆ พร้อมระบบคำนวณเส้นสะท้อน (Reflection) เพื่อช่วยวิเคราะห์มุมการยิงขั้นสูง

This is an advanced **Pool Guideline Overlay Tool** that helps visualize shot directions and bank shots (reflections) from the cue ball to all pockets.

---

## 🔄 อัพเดตล่าสุด (Latest Updates)
- **[NEW] ImGui-Style Settings UI:** กด `F2` เพื่อเปิดหน้าต่างตั้งค่าแบบ Real-time
- **[NEW] Reflection System:** เพิ่มจุดคำนวณเส้นสะท้อนชิ่งขอบโต๊ะ
- **[NEW] Customization:** ปรับแต่งแต่งขนาดลูก, ขนาดเส้น, ความโปร่งใส และสีสันได้ทุกจุด
- **[NEW] Custom Hotkeys:** ระบบเปลี่ยนคีย์ลัดได้ตามใจชอบ
- **[NEW] Reset to Defaults:** ปุ่มคืนค่าเริ่มต้นหากตั้งค่าผิดพลาด

---

# 🇹🇭 ภาษาไทย (Thai)

## 📌 เกี่ยวกับโปรแกรม

โปรแกรมนี้เป็น **Overlay Tool** ที่จะแสดงเส้นแนวการยิงบนหน้าจอ เพื่อช่วยให้ผู้เล่นวิเคราะห์มุมในการยิงลูกพูลไปยังหลุมต่าง ๆ 
ตัวโปรแกรมจะทำงานเป็น **หน้าต่างโปร่งใส (Transparent Overlay)** และสามารถวางทับบนหน้าต่างเกมเพลย์ได้โดยตรง 
ผู้ใช้สามารถลากตำแหน่งลูกขาว (Cue Ball) และจุดสะท้อน (Reflection Target) โปรแกรมจะทำการคำนวณเส้นฟิสิกส์ให้แบบ Real-time

---

## ✨ ฟีเจอร์หลัก

### 🎱 Pool Table Overlay
แสดงกรอบโต๊ะพูลบนหน้าจอ พร้อมเส้นขอบที่ปรับแต่งสีและความโปร่งใสได้

### 🎯 Auto Guideline & Reflection
- **Direct Shot:** วาดเส้นแนวเล็งจากลูกขาวไปยังหลุมทั้ง 6 หลุม (มุม 4, กลาง 2)
- **Bank Shot:** ระบบคำนวณเส้นสะท้อนขอบโต๊ะ (Reflection Vector) สำหรับการแทงชิ่ง

### ⚙️ Real-time Settings (F2)
หน้าต่างตั้งค่าแบบใหม่ที่ให้คุณปรับแต่ง:
- **ขนาดและสี:** รัศมีลูกขาว, ความหนาเส้นเล็ง, สีของจุดต่างๆ
- **ความโปร่งใส:** ปรับ Opacity ของพื้นหลังเพื่อไม่ให้บังเกม
- **คีย์ลัด (Hotkeys):** ตั้งค่าปุ่มกดใหม่ได้จากในโปรแกรม

### 🖱️ Edit Mode & 🔒 Lock Mode
- **โหมดแก้ไข:** สามารถใช้เมาส์ลากย้ายตำแหน่งลูกขาว, ย้ายจุดสะท้อน, และย่อขยายหน้าต่างได้
- **โหมดล็อค:** โปรแกรมจะ **ทะลุการคลิกเมาส์ (Click-through)** ทำให้คุณสามารถเล่นเกมที่อยู่ด้านหลังได้ตามปกติ โดยที่เส้นช่วยเล็งยังคงแสดงอยู่

### 💾 Auto-Save Config
โปรแกรมจะบันทึกการตั้งค่าทั้งหมดอัตโนมัติลงในไฟล์ `config.json`

---

## ⌨️ คีย์ลัดพื้นฐาน (Hotkeys)
*สามารถเปลี่ยนได้ในหน้าต่างตั้งค่า (F2)*

| ปุ่มกด (Key) | หน้าที่ (Function) |
|----|----|
| **Insert** | ล็อค / ปลดล็อคหน้าจอ (Lock / Unlock) |
| **F2** | เปิด / ปิด หน้าต่างตั้งค่า (Settings UI) |
| **F5** | บันทึกการตั้งค่า (Save Settings) |
| **F9** | สลับภาษา ไทย/English (Toggle Language) |
| **End** | ปิดโปรแกรม (Exit) |

---

# 🇺🇸 English

## 📌 About

This program is an advanced **Pool Aim Guideline Overlay Tool**. It draws aiming lines from the cue ball to every pocket on the table and calculates accurate reflection angles for bank shots. The application runs as a **transparent window** that stays on top of your game.

---

## ✨ Features

### 🎱 Pool Table Overlay
Displays a customizable virtual pool table border directly on your screen.

### 🎯 Auto Guideline & Reflection System
- **Direct Shots:** Automatically draws lines from the cue ball to all 6 pockets.
- **Bank Shots:** Moveable reflection point that calculates the exact vector bounce off the table cushions.

### ⚙️ Real-time Settings UI (F2)
A sleek, ImGui-inspired menu allows you to tweak:
- **Visuals:** Cue ball radius, reflection point size, line thickness, and all UI colors.
- **Opacity:** Adjust background transparency.
- **Hotkeys:** Rebind any action to a new key.

### 🖱️ Edit & 🔒 Lock Modes
- **Edit Mode:** Freely drag the cue ball, reflection target, or resize the overlay.
- **Lock Mode:** The overlay becomes **mouse-transparent**, allowing you to click and play the game underneath while the guidelines remain visible.

### 💾 Auto-Save
All configurations, including your custom hotkeys and colors, are saved automatically to `config.json`.

---

## ⌨️ Default Hotkeys
*Can be rebounded via the F2 Settings menu.*

| Key | Function |
|----|----|
| **Insert** | Lock / Unlock Overlay |
| **F2** | Open Settings UI |
| **F5** | Force Save Settings |
| **F9** | Switch Language (TH/EN) |
| **End** | Exit Program |

---

# 🚀 การติดตั้งและใช้งาน (Installation & Usage)

### 1️⃣ Install Python
Download and install Python 3.x from [python.org](https://python.org).

### 2️⃣ Install Dependencies
เปิด Command Prompt หรือ Terminal แล้วพิมพ์คำสั่ง:
```bash
pip install PyQt5 keyboard
