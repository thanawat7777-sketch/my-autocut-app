import os
import json
import uuid
import platform
import pandas as pd
import streamlit as st

from openai import OpenAI

# ----------------- 30 หมวดหมู่วิดีโอยอดนิยม -----------------
VIDEO_GENRES_30 = [
    {"id": 1, "name": "เรื่องเล่า / นิทานชีวิต (Storytelling)", "desc": "เล่าประสบการณ์จริง จุดเปลี่ยนชีวิต เปลี่ยนอารมณ์"},
    {"id": 2, "name": "หนังสั้น / ละครสั้นสอนใจ (Short Drama)", "desc": "เปิดด้วยจุดปะทะอารมณ์ ดำเนินเรื่อง สรุปข้อคิด"},
    {"id": 3, "name": "พอดแคสต์ตัดท่อนไวรัล (Podcast Highlights)", "desc": "ตัดไฮไลต์ประโยคเด็ด ซับไตเติลคาราโอเกะ"},
    {"id": 4, "name": "คำสอนธรรมะ / ข้อคิดเตือนสติ (Dharma & Quotes)", "desc": "ข้อคิดสงบจิตใจ วิวธรรมชาติ เพลงเบาสบาย"},
    {"id": 5, "name": "เรื่องผี / ประสบการณ์ลี้ลับ (Horror & Mystery)", "desc": "เล่าเรื่องชวนสงสัย เสียงหลอน ตัดจังหวะลุ้น"},
    {"id": 6, "name": "การเงิน / วางแผนการลงทุน (Personal Finance)", "desc": "ทริกออมเงิน ตัวเลขชัดเจน How-to ปลดหนี้"},
    {"id": 7, "name": "ให้ความรู้ / How-To 1 นาที (Micro-Learning)", "desc": "สอนเทคนิคสั้น กระชับ เข้าประเด็นทันที"},
    {"id": 8, "name": "จิตวิทยา / การอ่านใจคน (Psychology)", "desc": "วิเคราะห์พฤติกรรม สังเกตภาษากาย"},
    {"id": 9, "name": "สอนภาษา / สำนวนที่ใช้จริง (Language Tips)", "desc": "เปรียบเทียบคำที่ควรใช้และไม่ควรใช้ ซับ 2 ภาษา"},
    {"id": 10, "name": "สรุปข่าวสาร / เทรนด์ Tech & AI (News & Trends)", "desc": "อัปเดตเครื่องมือใหม่ ข่าวไว พาดหัวเด่น"},
    {"id": 11, "name": "รีวิวสินค้า / ป้ายยาของใช้ (Product Review)", "desc": "ชู Pain Point โชว์ของจริง บอกพิกัดซื้อ"},
    {"id": 12, "name": "Timelapse / งานศิลปะ / ประดิษฐ์ (Process)", "desc": "เร่งสปีดกระบวนการทำ รอดูผลงานตอนท้าย"},
    {"id": 13, "name": "Vlog 1 วัน (Day in the Life)", "desc": "เสียงพากย์ Voiceover สลับมุมกล้องไวๆ"},
    {"id": 14, "name": "พาเที่ยว / แจกแพลนเดินทาง (Travel Guide)", "desc": "ระบุงบ แจกพิกัด แผนที่ และมุมภาพสวย"},
    {"id": 15, "name": "พากิน / รีวิวร้านเด็ด (Foodie & Dining)", "desc": "ช็อตอาหารน่ากิน ASMR เสียงเคี้ยว/ปรุง"},
    {"id": 16, "name": "ออกกำลังกาย / ปั้นหุ่น (Fitness & Workout)", "desc": "ท่าทำตามง่าย มีตัวจับเวลานับถอยหลัง"},
    {"id": 17, "name": "ทำอาหารสุขภาพ / ลดน้ำหนัก (Healthy Cooking)", "desc": "แจกสูตรคลีน บอกแคลอรี Top-down view"},
    {"id": 18, "name": "สกินแคร์ / รักษาสิว / บิวตี้ (Beauty & Care)", "desc": "บอกส่วนผสม เตือนข้อห้าม โชว์ผิวจริง"},
    {"id": 19, "name": "จัดโต๊ะคอม / แต่งห้องมินิมอล (Room Setup)", "desc": "Before vs After ป้ายยาไอเทมแต่งห้อง"},
    {"id": 20, "name": "ปรับลุค / การแต่งตัว (Fashion & Grooming)", "desc": "กฎจับคู่สี เทคนิคแต่งตัวให้ดูสูง/ดูแพง"},
    {"id": 21, "name": "สัตว์เลี้ยงแสนรู้ / ตลกน่ารัก (Cute Pets)", "desc": "พากย์เสียงสัตว์ ช็อตซูมหน้าเรียกรอยยิ้ม"},
    {"id": 22, "name": "เบื้องหลังธุรกิจ / โรงงานผลิต (Behind Scenes)", "desc": "ความทุ่มเท กระบวนการทำสินค้าแบบเรียลๆ"},
    {"id": 23, "name": "สัมภาษณ์ข้างทาง (Street Interview)", "desc": "คำถามปั่นๆ หรือคำถามกระตุกต่อมคิด"},
    {"id": 24, "name": "ความสัมพันธ์ / คำแนะนำความรัก (Relationships)", "desc": "สัญญาณ Red/Green flags ข้อคิดชีวิตคู่"},
    {"id": 25, "name": "เกมมิ่ง / ไฮไลต์สตรีมเมอร์ (Gaming Highlights)", "desc": "ช็อตเด็ด คลัตช์เกม ตัดต่อเข้าบีตเพลง"},
    {"id": 26, "name": "ชาเลนจ์ / ทดลองทำ 7-30 วัน (Challenges)", "desc": "โชว์ผลการเปลี่ยนแปลงตามระยะเวลา"},
    {"id": 27, "name": "จับโป๊ะ / พิสูจน์คลิปไวรัล (Myth Busting)", "desc": "ทดสอบว่าของจริงหรือหลอกลวง"},
    {"id": 28, "name": "Life Hacks / ทริกลัดงานบ้าน (Life Hacks)", "desc": "วิธีแก้ปัญหาในบ้านที่จบไวใน 15 วินาที"},
    {"id": 29, "name": "แรงบันดาลใจ / ข้อคิดพลังบวก (Motivation)", "desc": "เสียงพากย์ทรงพลัง ดนตรียกระดับจิตใจ"},
    {"id": 30, "name": "ตอบคอมเมนต์แฟนคลับ / Q&A (Replying Comments)", "desc": "แปะแคปเจอร์คำถาม แล้วอธิบายเคลียร์ๆ"}
]

# ----------------- ฟังก์ชันหาโฟลเดอร์ CapCut -----------------
def get_capcut_draft_path():
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
    elif system == "Windows":  # Windows
        local_app = os.environ.get("LOCALAPPDATA", "")
        return os.path.join(local_app, "CapCut", "User Data", "Projects", "com.lveditor.draft")
    return os.path.abspath("./CapCut_Output_Drafts")

# ----------------- 1. เจนเนอเรตแผนคอนเทนต์ด้วย LLM -----------------
def generate_all_30_plans(niche: str, audience: str, api_key: str):
    client = OpenAI(api_key=api_key)
    prompt = f"""
    คุณเป็น Creative Director & Video Script Strategist สำหรับวิดีโอสั้นแนวตั้ง (TikTok, Reels, Shorts)
    สินค้า/หัวข้อหลัก: "{niche}"
    กลุ่มเป้าหมาย: "{audience}"

    จงคิดไอเดียคอนเทนต์วิดีโอให้ครบทั้ง 30 แนวต่อไปนี้:
    {json.dumps([g['name'] for g in VIDEO_GENRES_30], ensure_ascii=False)}

    ให้สร้างผลลัพธ์เป็น JSON Object ที่มีคีย์ "plans" เป็น List 30 รายการ โดยแต่ละรายการต้องมีฟิลด์:
    1. day (1 ถึง 30)
    2. genre (ชื่อแนววิดีโอตามลิสต์)
    3. topic (ชื่อเรื่องที่ดึงดูด)
    4. hook_screen (ข้อความพาดหัวตัวใหญ่บนหน้าจอ 3 วินาทีแรก)
    5. script (บทพูดความยาวประมาณ 30-45 วินาที พร้อมระบุ [Hook], [Body], [CTA])
    6. heading_highlight (ข้อความป้าย Tag กลางคลิป เช่น 'สารอาหารครบ 5 หมู่', '3 สเต็ปง่ายๆ')
    7. cta (ประโยค Call-to-Action ท้ายคลิป)
    8. caption (ข้อความแคปชันสำหรับโพสต์)
    9. hashtags (ลิสต์ 5-7 แฮชแท็ก)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content).get("plans", [])

# ----------------- 2. ตัดต่อและสร้างโปรเจกต์ CapCut -----------------
def process_video_and_build_draft(video_path: str, project_name: str, hook_text: str, heading_text: str):
    # 1. รัน Faster-Whisper + VAD ตัด Dead Air
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        video_path,
        language="th",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )

    transcript = []
    for s in segments:
        txt = s.text.strip()
        if txt:
            transcript.append({"start": s.start, "end": s.end, "text": txt})

    if not transcript:
        raise ValueError("ไม่พบเสียงพูดในคลิป หรือเสียงเบาเกินไป")

    # 2. เตรียมโฟลเดอร์ CapCut Draft
    base_dir = get_capcut_draft_path()
    os.makedirs(base_dir, exist_ok=True)
    draft_id = str(uuid.uuid4()).upper()
    proj_dir = os.path.join(base_dir, draft_id)
    os.makedirs(proj_dir, exist_ok=True)

    video_material_id = str(uuid.uuid4())
    video_segments = []
    subtitle_segments = []
    text_materials = []

    current_timeline_us = 0
    for item in transcript:
        dur_us = int((item["end"] - item["start"]) * 1_000_000)
        src_start_us = int(item["start"] * 1_000_000)

        # Video track (กระโดดข้าม Dead Air)
        video_segments.append({
            "id": str(uuid.uuid4()),
            "material_id": video_material_id,
            "source_timerange": {"start": src_start_us, "duration": dur_us},
            "target_timerange": {"start": current_timeline_us, "duration": dur_us}
        })

        # Subtitle track (Noto Sans Thai)
        t_id = str(uuid.uuid4())
        text_materials.append({
            "id": t_id,
            "content": json.dumps({"text": item["text"], "styles": [{"font": {"name": "Noto Sans Thai"}}]}),
            "type": "subtitle"
        })
        subtitle_segments.append({
            "id": str(uuid.uuid4()),
            "material_id": t_id,
            "target_timerange": {"start": current_timeline_us, "duration": dur_us}
        })

        current_timeline_us += dur_us

    # 3. ใส่ Hook Text (ช่วง 0-3 วินาทีแรก)
    if hook_text:
        h_id = str(uuid.uuid4())
        text_materials.append({
            "id": h_id,
            "content": json.dumps({"text": hook_text, "styles": [{"font": {"name": "Noto Sans Thai"}, "size": 16.0}]}),
            "type": "heading"
        })
        subtitle_segments.append({
            "id": str(uuid.uuid4()),
            "material_id": h_id,
            "target_timerange": {"start": 0, "duration": min(3_000_000, current_timeline_us)}
        })

    # 4. ใส่ Heading Card ไฮไลต์ (ช่วงกลางคลิป)
    if heading_text and current_timeline_us > 4_000_000:
        card_id = str(uuid.uuid4())
        text_materials.append({
            "id": card_id,
            "content": json.dumps({"text": heading_text, "styles": [{"font": {"name": "Noto Sans Thai"}, "size": 13.0}]}),
            "type": "heading"
        })
        subtitle_segments.append({
            "id": str(uuid.uuid4()),
            "material_id": card_id,
            "target_timerange": {"start": 3_500_000, "duration": min(4_000_000, current_timeline_us - 3_500_000)}
        })

    # 5. ประกอบ draft_content.json
    draft_data = {
        "id": draft_id,
        "name": project_name,
        "fps": 30.0,
        "duration": current_timeline_us,
        "canvas_config": {"width": 1080, "height": 1920, "ratio": "9:16"},
        "materials": {
            "videos": [{"id": video_material_id, "path": os.path.abspath(video_path), "type": "video"}],
            "texts": text_materials
        },
        "tracks": [
            {"id": str(uuid.uuid4()), "type": "video", "segments": video_segments},
            {"id": str(uuid.uuid4()), "type": "text", "segments": subtitle_segments}
        ]
    }

    with open(os.path.join(proj_dir, "draft_content.json"), "w", encoding="utf-8") as f:
        json.dump(draft_data, f, ensure_ascii=False, indent=2)

    return proj_dir, transcript

# ----------------- ส่วนหน้าจอ Streamlit UI -----------------
st.set_page_config(page_title="AI 30-Day Video Studio & CapCut AutoCut", page_icon="⚡", layout="wide")

st.title("⚡ AI Content Studio: 30 วัน 30 แนววิดีโอ + ตัดต่อส่งตรงเข้า CapCut")
