"""
Vercel Serverless Entrypoint (api/index.py)
FingerVision Quality Control API Endpoint
"""
import os
import sys
import json
import base64
import numpy as np
import cv2
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path to import quality_assessment.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quality_assessment import quality_gate, DEFAULT_THRESHOLDS

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            "status": "online",
            "system": "FingerVision Quality Control System",
            "version": "1.0",
            "engine": "OpenCV + NumPy Biometric Quality Gate",
            "thresholds": DEFAULT_THRESHOLDS,
            "endpoints": {
                "health": "GET /",
                "assess": "POST / (body JSON: {'image': 'base64_string'})"
            }
        }
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
        return

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            b64_str = payload.get("image", "")
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
                
            img_bytes = base64.b64decode(b64_str)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                raise ValueError("Could not decode image from provided base64 string.")
                
            result = quality_gate(img_bgr)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            err_resp = {"error": str(e), "status": "failed"}
            self.wfile.write(json.dumps(err_resp).encode('utf-8'))
        return
