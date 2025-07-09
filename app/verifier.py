import pytesseract
from pyzbar.pyzbar import decode
from PIL import Image as PILImage
import imagehash
import os
from pdf2image import convert_from_path


def match_stamp(uploaded_path, reference_path, threshold=36):
    try:
        uploaded_full = PILImage.open(uploaded_path).convert("RGB")
        width, height = uploaded_full.size

        # Crop bottom-right corner (adjust if needed)
        crop_box = (width - 300, height - 300, width, height)
        uploaded_crop = uploaded_full.crop(crop_box).resize((200, 200))

        reference_image = PILImage.open(reference_path).convert("RGB").resize((200, 200))

        uploaded_hash = imagehash.phash(uploaded_crop)
        reference_hash = imagehash.phash(reference_image)

        diff = uploaded_hash - reference_hash
        print(f"[STAMP MATCH] Hash difference: {diff} | Threshold: {threshold} | MATCH: {diff <= threshold}")

        return diff <= threshold
    except Exception as e:
        print("Stamp matching error:", e)
        return False


def analyze_document(filepath):
    result = {
        "status": "Unknown",
        "message": "",
        "ocr_text": "",
        "qr_data": "",
        "file": filepath
    }

    temp_image_path = None

    try:
        file_ext = os.path.splitext(filepath)[1].lower()

        # Step 1: Load the file as image
        if file_ext == ".pdf":
            images = convert_from_path(filepath, dpi=300)
            if not images:
                result["message"] = "No pages found in PDF."
                return result
            pil_image = images[0].convert("L")  # Grayscale
        else:
            pil_image = PILImage.open(filepath).convert("L")

        # Save image temporarily for QR + stamp matching
        temp_image_path = filepath + "_converted.png"
        pil_image.convert("RGB").save(temp_image_path)

        # Step 2: OCR
        text = pytesseract.image_to_string(pil_image)
        result["ocr_text"] = text.strip()

        # Step 3: QR Code Detection
        try:
            qr_codes = decode(PILImage.open(temp_image_path))
            if qr_codes:
                result["qr_data"] = qr_codes[0].data.decode("utf-8")
                result["status"] = "Valid QR Found"
                result["message"] = "QR code decoded."
            else:
                result["status"] = "No QR Code"
                result["message"] = "OCR completed, but no QR code detected."
        except Exception as qr_error:
            result["message"] += f" QR check error: {qr_error}"

        # Step 4: Keyword-Based Authenticity Check
        known_issuers = [
            "University of Johannesburg",
            "Certified Copy",
            "This is to certify that",
            "National Diploma",
            "Academic Transcript",
            "Department of Home Affairs",
            "South African Qualifications Authority",
            "Bachelor", "Diploma", "National Certificate"
        ]

        match_score = sum(issuer in result["ocr_text"] for issuer in known_issuers)

        # Step 5: UJ Stamp Match
        stamp_path = "stamps_dataset/University/image1.png"
        stamp_matched = os.path.exists(stamp_path) and match_stamp(temp_image_path, stamp_path)

        if match_score >= 2 and stamp_matched:
            result["status"] = "Verified"
            result["message"] += f" Document text appears authentic ({match_score} trusted phrases found). UJ stamp recognized."
        elif match_score >= 2:
            result["status"] = "Partial Match"
            result["message"] += f" Document text appears authentic ({match_score} trusted phrases found), but UJ stamp not detected."
        elif stamp_matched:
            result["status"] = "Suspicious"
            result["message"] += " UJ stamp detected, but text format seems inconsistent."
        else:
            result["status"] = "Unverified"
            result["message"] += " No stamp or official keywords detected."

    except Exception as e:
        result["status"] = "Error"
        result["message"] = f"Unexpected error: {str(e)}"

    finally:
        # Clean up temp image
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    return result
