#!/usr/bin/env python3
"""
ShuttleSync AI Biomechanical Analysis Engine
Uses MediaPipe Pose + Hands for badminton stroke analysis
"""
import sys
import json
import math
import os
import tempfile

import cv2
import numpy as np
import mediapipe as mp


class BadmintonAnalyzer:
    """Analyzes badminton strokes using MediaPipe Pose + Hands."""

    # MediaPipe Pose landmark indices
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    NOSE = 0
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22

    # Reference skeleton connections for drawing
    SKELETON_CONNECTIONS = [
        (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
        (11, 23), (12, 24), (23, 24), (23, 25), (24, 26),
        (25, 27), (26, 28), (0, 11), (0, 12),
    ]

    # Reference skeleton poses (normalized x,y in 0-1 range)
    # Each pose represents the ideal form for a badminton shot
    REFERENCE_POSES = {
        "Smash": {
            "landmarks": {
                0: (0.48, 0.08),   # nose
                11: (0.38, 0.22),  # left shoulder
                12: (0.58, 0.20),  # right shoulder (raised)
                13: (0.30, 0.18),  # left elbow
                14: (0.68, 0.10),  # right elbow (high)
                15: (0.25, 0.25),  # left wrist
                16: (0.72, 0.03),  # right wrist (above head)
                23: (0.42, 0.45),  # left hip
                24: (0.54, 0.44),  # right hip
                25: (0.38, 0.65),  # left knee
                26: (0.58, 0.60),  # right knee (slightly bent for jump)
                27: (0.35, 0.85),  # left ankle
                28: (0.62, 0.78),  # right ankle
            },
            "ideal_angles": {
                "right_elbow": 170, "left_elbow": 130,
                "right_hip": 165, "left_hip": 170,
                "right_knee": 135, "left_knee": 145,
                "right_shoulder": 160, "left_shoulder": 100,
            },
            "description": "Reach high with racket arm extended. Elbow locked at contact. Wrist above shoulder.",
            "key_points": ["Wrist above head", "Elbow near-straight", "Hip rotation 20-60°", "Knees bent for jump"],
        },
        "Serve": {
            "landmarks": {
                0: (0.48, 0.15),
                11: (0.40, 0.30),
                12: (0.56, 0.30),
                13: (0.32, 0.38),
                14: (0.62, 0.40),  # racket arm lower
                15: (0.28, 0.48),
                16: (0.55, 0.52),  # wrist below waist
                23: (0.43, 0.52),
                24: (0.53, 0.52),
                25: (0.40, 0.70),
                26: (0.55, 0.68),
                27: (0.37, 0.88),
                28: (0.58, 0.87),
            },
            "ideal_angles": {
                "right_elbow": 120, "left_elbow": 100,
                "right_hip": 160, "left_hip": 155,
                "right_knee": 140, "left_knee": 135,
                "right_shoulder": 110, "left_shoulder": 95,
            },
            "description": "Low stance, wrist below waist for legal serve. Controlled arm position.",
            "key_points": ["Wrist below waist", "Low stance", "Shoulder-width feet", "Controlled torso"],
        },
        "Cross Drop": {
            "landmarks": {
                0: (0.48, 0.10),
                11: (0.40, 0.24),
                12: (0.56, 0.24),  # shoulders square
                13: (0.34, 0.22),
                14: (0.64, 0.20),
                15: (0.30, 0.28),
                16: (0.70, 0.15),  # racket prep height
                23: (0.43, 0.46),
                24: (0.53, 0.46),
                25: (0.40, 0.65),
                26: (0.56, 0.63),
                27: (0.37, 0.85),
                28: (0.59, 0.83),
            },
            "ideal_angles": {
                "right_elbow": 130, "left_elbow": 125,
                "right_hip": 168, "left_hip": 172,
                "right_knee": 145, "left_knee": 150,
                "right_shoulder": 135, "left_shoulder": 130,
            },
            "description": "Shoulders square for deception. Racket preparation height. Controlled hip position.",
            "key_points": ["Shoulders square", "Racket high", "Minimal hip rotation", "Balanced lunge"],
        },
        "Net Play": {
            "landmarks": {
                0: (0.45, 0.12),
                11: (0.38, 0.26),
                12: (0.54, 0.26),
                13: (0.32, 0.30),
                14: (0.65, 0.22),
                15: (0.28, 0.35),
                16: (0.78, 0.18),  # extended forward
                23: (0.42, 0.48),
                24: (0.52, 0.48),
                25: (0.36, 0.62),  # deep lunge
                26: (0.60, 0.58),
                27: (0.32, 0.80),
                28: (0.65, 0.72),
            },
            "ideal_angles": {
                "right_elbow": 160, "left_elbow": 110,
                "right_hip": 100, "left_hip": 105,
                "right_knee": 90, "left_knee": 140,
                "right_shoulder": 150, "left_shoulder": 90,
            },
            "description": "Deep lunge, arm extended forward. Racket-side leg leading. Stable base.",
            "key_points": ["Deep lunge", "Arm extended", "Racket leg forward", "Centered torso"],
        },
        "General Play": {
            "landmarks": {
                0: (0.48, 0.10),
                11: (0.40, 0.24),
                12: (0.56, 0.24),
                13: (0.34, 0.32),
                14: (0.62, 0.32),
                15: (0.30, 0.38),
                16: (0.66, 0.38),
                23: (0.43, 0.46),
                24: (0.53, 0.46),
                25: (0.40, 0.64),
                26: (0.56, 0.64),
                27: (0.37, 0.84),
                28: (0.59, 0.84),
            },
            "ideal_angles": {
                "right_elbow": 135, "left_elbow": 130,
                "right_hip": 165, "left_hip": 165,
                "right_knee": 145, "left_knee": 145,
                "right_shoulder": 120, "left_shoulder": 115,
            },
            "description": "Athletic ready position. Feet shoulder-width apart. Knees bent.",
            "key_points": ["Shoulder-width stance", "Knees bent", "Centered balance", "Arms ready"],
        },
    }

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

    def preprocess_image(self, image):
        """Enhance image for better MediaPipe detection."""
        h, w = image.shape[:2]

        # Upscale small images (MediaPipe works best on 500px+ faces)
        min_dim = min(h, w)
        if min_dim < 400:
            scale = 400 / min_dim
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            h, w = image.shape[:2]

        # Convert to LAB for CLAHE contrast enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(l_channel)
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # Light sharpening to improve edge detection
        kernel = np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]])
        image = cv2.filter2D(image, -1, kernel)

        return image

    def check_image_quality(self, image):
        """Check image quality and return warnings + quality score."""
        h, w = image.shape[:2]
        warnings = []
        quality_score = 100

        # Resolution check
        total_pixels = h * w
        if total_pixels < 200000:  # < ~450x450
            warnings.append("Low resolution image. For best results, use photos with at least 1MP (1024x768).")
            quality_score -= 30
        elif total_pixels < 500000:  # < ~700x700
            warnings.append("Medium resolution. A higher resolution photo will improve accuracy.")
            quality_score -= 10

        # Aspect ratio check (extreme crops are hard to analyze)
        aspect = max(w, h) / min(w, h)
        if aspect > 2.5:
            warnings.append("Extreme aspect ratio detected. A full-body photo works best.")
            quality_score -= 15

        # Blur detection (Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50:
            warnings.append("Image appears blurry. A sharper photo will give more accurate results.")
            quality_score -= 25
        elif laplacian_var < 150:
            warnings.append("Image is slightly soft. Try to use a sharper photo.")
            quality_score -= 10

        # Brightness check
        mean_brightness = np.mean(gray)
        if mean_brightness < 40:
            warnings.append("Image is too dark. Better lighting will improve detection.")
            quality_score -= 20
        elif mean_brightness > 220:
            warnings.append("Image is overexposed. Reduce brightness for better results.")
            quality_score -= 15

        # Contrast check
        contrast = np.std(gray)
        if contrast < 30:
            warnings.append("Low contrast image. Ensure good lighting contrast between subject and background.")
            quality_score -= 15

        return max(0, quality_score), warnings

    def calculate_angle(self, point_a, point_b, point_c):
        """Calculate angle at point_b formed by point_a -> point_b -> point_c."""
        a = np.array(point_a)
        b = np.array(point_b)
        c = np.array(point_c)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
        return round(float(angle), 1)

    def calculate_distance(self, point_a, point_b):
        """Calculate Euclidean distance between two points."""
        a = np.array(point_a)
        b = np.array(point_b)
        return float(np.linalg.norm(a - b))

    def get_landmark_coords(self, landmarks, idx, img_w, img_h):
        """Get pixel coordinates for a landmark."""
        lm = landmarks[idx]
        return (lm.x * img_w, lm.y * img_h)

    def analyze_pose(self, image_path):
        """Run MediaPipe Pose + Hands and return landmarks."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Check quality before preprocessing
        quality_score, quality_warnings = self.check_image_quality(image)

        # Preprocess for better detection
        image = self.preprocess_image(image)
        img_h, img_w = image.shape[:2]
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pose_results = None
        hand_results = None
        hand_landmarks_list = []

        # Run Pose with confidence levels — don't go too low or partial faces slip through
        for confidence in [0.6, 0.5, 0.4]:
            with self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                min_detection_confidence=confidence,
            ) as pose:
                pose_results = pose.process(rgb)
            if pose_results and pose_results.pose_landmarks:
                break

        # Run Hands
        with self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.3,
        ) as hands:
            hand_results = hands.process(rgb)

        if not pose_results or not pose_results.pose_landmarks:
            return None, img_w, img_h, [], quality_score, quality_warnings

        pose_lm = pose_results.pose_landmarks.landmark

        # ---- FULL BODY VALIDATION ----
        # Require all major body regions visible: head, shoulders, hips, knees, ankles
        UPPER_BODY = [0, 11, 12, 13, 14, 15, 16]   # nose, shoulders, elbows, wrists
        LOWER_BODY = [23, 24, 25, 26, 27, 28]       # hips, knees, ankles
        ALL_KEY = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

        upper_vis = [pose_lm[i].visibility for i in UPPER_BODY if i < len(pose_lm)]
        lower_vis = [pose_lm[i].visibility for i in LOWER_BODY if i < len(pose_lm)]
        all_vis = [pose_lm[i].visibility for i in ALL_KEY if i < len(pose_lm)]

        avg_visibility = sum(all_vis) / len(all_vis) if all_vis else 0
        avg_lower_vis = sum(lower_vis) / len(lower_vis) if lower_vis else 0
        avg_upper_vis = sum(upper_vis) / len(upper_vis) if upper_vis else 0

        # Count how many key landmarks are confidently visible (threshold 0.5)
        well_visible = sum(1 for v in all_vis if v > 0.5)
        lower_visible = sum(1 for v in lower_vis if v > 0.5)

        # Check body span: head-to-toe should cover at least 50% of image height
        y_coords = [pose_lm[i].y for i in ALL_KEY if i < len(pose_lm)]
        body_span = (max(y_coords) - min(y_coords)) if len(y_coords) >= 2 else 0

        # REJECT: No lower body landmarks visible at all
        if lower_visible == 0:
            return None, img_w, img_h, [], quality_score, [
                "Full body not detected. Only upper body / face was found. "
                "Please stand back so your entire body (head to toe) is visible in the frame."
            ]

        # REJECT: Lower body landmarks have very poor confidence
        if avg_lower_vis < 0.3:
            return None, img_w, img_h, [], quality_score, [
                "Lower body (hips, knees, feet) is not clearly visible. "
                "Ensure your full body from head to toe is in the frame with good lighting."
            ]

        # WARNING: Body doesn't span enough of the frame (partial body)
        if body_span < 0.40:
            quality_warnings.append(
                "Only a portion of your body is visible. "
                "Step back so your full body (head to toe) fills most of the frame."
            )
            quality_score = max(0, quality_score - 25)

        # WARNING: Too few well-visible landmarks
        if well_visible < 8:
            quality_warnings.append(
                f"Only {well_visible}/13 key body points clearly visible. "
                "Ensure good lighting and that your entire body is facing the camera."
            )
            quality_score = max(0, quality_score - 15)

        # General visibility feedback
        if avg_visibility < 0.4:
            quality_warnings.append("Body detection confidence is low. Ensure the full body is clearly visible.")
            quality_score = max(0, quality_score - 20)
        elif avg_visibility < 0.6:
            quality_warnings.append("Some body parts may be partially occluded.")
            quality_score = max(0, quality_score - 10)

        if hand_results and hand_results.multi_hand_landmarks:
            for hand_lms in hand_results.multi_hand_landmarks:
                hand_landmarks_list.append(hand_lms.landmark)

        return pose_lm, img_w, img_h, hand_landmarks_list, quality_score, quality_warnings

    def extract_body_metrics(self, pose_lm, img_w, img_h):
        """Extract body joint angles and positions from pose landmarks."""
        def coord(idx):
            return self.get_landmark_coords(pose_lm, idx, img_w, img_h)

        # Joint angles
        right_shoulder_angle = self.calculate_angle(
            coord(self.RIGHT_HIP), coord(self.RIGHT_SHOULDER), coord(self.RIGHT_ELBOW)
        )
        left_shoulder_angle = self.calculate_angle(
            coord(self.LEFT_HIP), coord(self.LEFT_SHOULDER), coord(self.LEFT_ELBOW)
        )

        right_elbow_angle = self.calculate_angle(
            coord(self.RIGHT_SHOULDER), coord(self.RIGHT_ELBOW), coord(self.RIGHT_WRIST)
        )
        left_elbow_angle = self.calculate_angle(
            coord(self.LEFT_SHOULDER), coord(self.LEFT_ELBOW), coord(self.LEFT_WRIST)
        )

        right_hip_angle = self.calculate_angle(
            coord(self.RIGHT_SHOULDER), coord(self.RIGHT_HIP), coord(self.RIGHT_KNEE)
        )
        left_hip_angle = self.calculate_angle(
            coord(self.LEFT_SHOULDER), coord(self.LEFT_HIP), coord(self.LEFT_KNEE)
        )

        right_knee_angle = self.calculate_angle(
            coord(self.RIGHT_HIP), coord(self.RIGHT_KNEE), coord(self.RIGHT_ANKLE)
        )
        left_knee_angle = self.calculate_angle(
            coord(self.LEFT_HIP), coord(self.LEFT_KNEE), coord(self.LEFT_ANKLE)
        )

        # Torso lean (vertical alignment)
        mid_shoulder = (
            (coord(self.LEFT_SHOULDER)[0] + coord(self.RIGHT_SHOULDER)[0]) / 2,
            (coord(self.LEFT_SHOULDER)[1] + coord(self.RIGHT_SHOULDER)[1]) / 2,
        )
        mid_hip = (
            (coord(self.LEFT_HIP)[0] + coord(self.RIGHT_HIP)[0]) / 2,
            (coord(self.LEFT_HIP)[1] + coord(self.RIGHT_HIP)[1]) / 2,
        )
        torso_lean = abs(mid_shoulder[0] - mid_hip[0])

        # Stance width (distance between feet)
        stance_width = self.calculate_distance(coord(self.LEFT_ANKLE), coord(self.RIGHT_ANKLE))

        # Shoulder width for reference
        shoulder_width = self.calculate_distance(coord(self.LEFT_SHOULDER), coord(self.RIGHT_SHOULDER))

        # Arm extension (distance from wrist to opposite hip, higher = more extended)
        right_arm_extension = self.calculate_distance(coord(self.RIGHT_WRIST), coord(self.LEFT_HIP))
        left_arm_extension = self.calculate_distance(coord(self.LEFT_WRIST), coord(self.RIGHT_HIP))

        # Wrist height relative to shoulders (negative = above head)
        avg_shoulder_y = (coord(self.LEFT_SHOULDER)[1] + coord(self.RIGHT_SHOULDER)[1]) / 2
        right_wrist_y = coord(self.RIGHT_WRIST)[1]
        left_wrist_y = coord(self.LEFT_WRIST)[1]

        # Nose to wrist distance (for reach analysis)
        nose = coord(self.NOSE)
        right_reach = self.calculate_distance(nose, coord(self.RIGHT_WRIST))
        left_reach = self.calculate_distance(nose, coord(self.LEFT_WRIST))

        return {
            "right_shoulder_angle": right_shoulder_angle,
            "left_shoulder_angle": left_shoulder_angle,
            "right_elbow_angle": right_elbow_angle,
            "left_elbow_angle": left_elbow_angle,
            "right_hip_angle": right_hip_angle,
            "left_hip_angle": left_hip_angle,
            "right_knee_angle": right_knee_angle,
            "left_knee_angle": left_knee_angle,
            "torso_lean": round(torso_lean, 1),
            "stance_width": round(stance_width, 1),
            "shoulder_width": round(shoulder_width, 1),
            "right_arm_extension": round(right_arm_extension, 1),
            "left_arm_extension": round(left_arm_extension, 1),
            "right_wrist_above_shoulder": right_wrist_y < avg_shoulder_y,
            "left_wrist_above_shoulder": left_wrist_y < avg_shoulder_y,
            "right_reach": round(right_reach, 1),
            "left_reach": round(left_reach, 1),
        }

    def extract_hand_metrics(self, hand_landmarks_list, img_w, img_h):
        """Extract hand grip and finger metrics."""
        if not hand_landmarks_list:
            return {"hands_detected": 0}

        hands_data = []
        for hand_lms in hand_landmarks_list:
            def coord(idx):
                return (hand_lms[idx].x * img_w, hand_lms[idx].y * img_h)

            # Wrist to middle fingertip distance (grip reach)
            wrist = coord(0)
            middle_tip = coord(12)
            grip_reach = self.calculate_distance(wrist, middle_tip)

            # Finger spread (distance between thumb and index tips)
            thumb_tip = coord(4)
            index_tip = coord(8)
            pinky_tip = coord(20)
            finger_spread = self.calculate_distance(thumb_tip, index_tip)

            # Fist tightness (distance from wrist to palm center)
            palm_center = (
                (coord(0)[0] + coord(9)[0]) / 2,
                (coord(0)[1] + coord(9)[1]) / 2,
            )
            palm_center_dist = self.calculate_distance(wrist, coord(9))

            # Finger curl (distance from fingertip to MCP joint)
            index_mcp = coord(5)
            index_curl = self.calculate_distance(index_tip, index_mcp)

            middle_mcp = coord(9)
            middle_curl = self.calculate_distance(middle_tip, middle_mcp)

            hands_data.append({
                "grip_reach": round(grip_reach, 2),
                "finger_spread": round(finger_spread, 2),
                "palm_distance": round(palm_center_dist, 2),
                "index_curl": round(index_curl, 2),
                "middle_curl": round(middle_curl, 2),
            })

        return {
            "hands_detected": len(hands_data),
            "hands": hands_data,
        }

    def normalize_landmarks(self, pose_lm, img_w, img_h):
        """Normalize landmarks to 0-1 range based on body bounding box."""
        coords = {}
        important = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in important:
            lm = pose_lm[idx]
            coords[idx] = (lm.x, lm.y)
        
        xs = [c[0] for c in coords.values()]
        ys = [c[1] for c in coords.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max_x - min_x or 1.0
        range_y = max_y - min_y or 1.0
        
        normalized = {}
        for idx, (x, y) in coords.items():
            normalized[idx] = (
                round((x - min_x) / range_x, 3),
                round((y - min_y) / range_y, 3),
            )
        return normalized

    def calculate_similarity(self, user_norm, reference_landmarks):
        """Compare user pose to reference and return similarity score + per-joint errors.
        Key joints (shoulders, wrists, hips, knees) are weighted more heavily."""
        # Weights: higher = more important for scoring
        WEIGHTS = {
            0: 1.5,   # nose (head position)
            11: 2.0,  # left shoulder
            12: 2.0,  # right shoulder
            13: 1.5,  # left elbow
            14: 1.5,  # right elbow
            15: 2.5,  # left wrist (racket hand position is critical)
            16: 2.5,  # right wrist
            23: 1.5,  # left hip
            24: 1.5,  # right hip
            25: 2.0,  # left knee
            26: 2.0,  # right knee
            27: 1.0,  # left ankle
            28: 1.0,  # right ankle
        }
        
        total_error = 0
        total_weight = 0
        joint_errors = {}
        
        for idx, ref_pos in reference_landmarks.items():
            if idx in user_norm:
                user_pos = user_norm[idx]
                error = math.sqrt((user_pos[0] - ref_pos[0])**2 + (user_pos[1] - ref_pos[1])**2)
                joint_errors[idx] = round(error, 3)
                w = WEIGHTS.get(idx, 1.0)
                total_error += error * w
                total_weight += w
        
        avg_error = total_error / total_weight if total_weight > 0 else 1.0
        # Convert error to similarity (0-100): 0 error = 100%, 0.6+ error = 0%
        # Using 0.6 threshold gives more reasonable spread
        similarity = max(0, min(100, round((1 - avg_error / 0.6) * 100)))
        
        return similarity, joint_errors

    def extract_detected_skeleton(self, pose_lm, img_w, img_h):
        """Extract detected skeleton coordinates for frontend rendering."""
        landmarks = {}
        important = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        for idx in important:
            lm = pose_lm[idx]
            landmarks[str(idx)] = {
                "x": round(lm.x, 4),
                "y": round(lm.y, 4),
                "visibility": round(lm.visibility, 3) if hasattr(lm, 'visibility') else 1.0,
            }
        
        connections = [[a, b] for a, b in self.SKELETON_CONNECTIONS]
        return {"landmarks": landmarks, "connections": connections}

    def auto_detect_shot_type(self, body, hands):
        """Analyze body metrics and determine the most likely shot type.
        Returns (detected_type, confidence, all_scores) where all_scores
        is a dict of {shot_type: similarity_score} for each reference."""
        
        scores = {}
        user_norm_sample = None  # We'll use body metrics for detection

        # --- Score each shot type based on body characteristics ---
        
        # Smash indicators: wrist above shoulder, high arm extension, hip rotation
        smash_score = 0
        if body["right_wrist_above_shoulder"] or body["left_wrist_above_shoulder"]:
            smash_score += 30
        arm_ext = max(body["right_arm_extension"], body["left_arm_extension"])
        if arm_ext > 160: smash_score += 25
        elif arm_ext > 130: smash_score += 15
        hip_rot = abs(body["right_hip_angle"] - body["left_hip_angle"])
        if 15 < hip_rot < 70: smash_score += 20
        elbow = max(body["right_elbow_angle"], body["left_elbow_angle"])
        if elbow > 150: smash_score += 15
        knee = min(body["right_knee_angle"], body["left_knee_angle"])
        if knee < 150: smash_score += 10
        scores["Smash"] = min(100, smash_score)

        # Serve indicators: wrist below waist (not above shoulder), controlled stance
        serve_score = 0
        wrist_below = not body["right_wrist_above_shoulder"] and not body["left_wrist_above_shoulder"]
        if wrist_below: serve_score += 30
        if knee > 130: serve_score += 15  # more upright
        stance_ratio = body["stance_width"] / body["shoulder_width"] if body["shoulder_width"] > 0 else 0
        if 0.7 < stance_ratio < 1.4: serve_score += 20
        if arm_ext < body["shoulder_width"] * 1.8: serve_score += 15
        if body["torso_lean"] < body["shoulder_width"] * 0.3: serve_score += 10
        scores["Serve"] = min(100, serve_score)

        # Cross Drop indicators: shoulders square, wrist high but controlled, minimal hip rotation
        drop_score = 0
        shoulder_sq = abs(body["right_shoulder_angle"] - body["left_shoulder_angle"])
        if shoulder_sq < 25: drop_score += 30  # square shoulders = deception
        if body["right_wrist_above_shoulder"] or body["left_wrist_above_shoulder"]: drop_score += 20
        if hip_rot < 30: drop_score += 20  # stable hips = deception
        elbow_min = min(body["right_elbow_angle"], body["left_elbow_angle"])
        if 90 < elbow_min < 160: drop_score += 15  # controlled arm angle
        if knee > 130: drop_score += 10  # not deep lunge
        scores["Cross Drop"] = min(100, drop_score)

        # Net Play indicators: deep lunge, arm extended forward, hip compression
        net_score = 0
        if knee < 100: net_score += 35  # deep lunge
        elif knee < 130: net_score += 20
        hip_min = min(body["right_hip_angle"], body["left_hip_angle"])
        if hip_min < 110: net_score += 25  # hip compression
        if arm_ext > 150: net_score += 20  # extended arm
        elif arm_ext > 120: net_score += 10
        if stance_ratio > 1.0: net_score += 10  # wide stance in lunge
        scores["Net Play"] = min(100, net_score)

        # General Play: balanced ready position
        general_score = 0
        if 0.9 < stance_ratio < 1.6: general_score += 25
        if 120 < knee < 170: general_score += 20  # athletic knee bend
        if body["torso_lean"] < body["shoulder_width"] * 0.25: general_score += 20
        if arm_ext < body["shoulder_width"] * 2.2: general_score += 15
        general_score += 10  # base score for neutral stance
        scores["General Play"] = min(100, general_score)

        # Determine best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # If best score is too low, default to General Play
        if best_score < 20:
            best_type = "General Play"
            best_score = scores["General Play"]

        confidence = min(100, best_score)
        
        return best_type, confidence, scores

    def get_reference_skeleton(self, shot_type):
        """Get reference skeleton data for the frontend guide."""
        ref = self.REFERENCE_POSES.get(shot_type, self.REFERENCE_POSES["General Play"])
        landmarks = {}
        for idx, (x, y) in ref["landmarks"].items():
            landmarks[str(idx)] = {"x": x, "y": y}
        
        connections = [[a, b] for a, b in self.SKELETON_CONNECTIONS]
        return {
            "landmarks": landmarks,
            "connections": connections,
            "description": ref["description"],
            "key_points": ref["key_points"],
            "ideal_angles": ref["ideal_angles"],
        }

    def score_shot(self, shot_type, body, hands):
        """Score and provide feedback based on shot type and metrics."""
        scores = {}
        feedback = []

        if shot_type == "Smash":
            # Smash: high arm extension, elbow near-straight, wrist above shoulder
            arm_ext = max(body["right_arm_extension"], body["left_arm_extension"])
            elbow = max(body["right_elbow_angle"], body["left_elbow_angle"])
            wrist_above = body["right_wrist_above_shoulder"] or body["left_wrist_above_shoulder"]
            hip_rot = abs(body["right_hip_angle"] - body["left_hip_angle"])

            # Arm extension score (150+ optimal for smash)
            if arm_ext > 180:
                scores["arm_extension"] = min(100, 90 + (arm_ext - 180) * 0.2)
                feedback.append("Excellent arm extension at contact.")
            elif arm_ext > 140:
                scores["arm_extension"] = 70 + (arm_ext - 140) * 0.5
                feedback.append("Good arm reach, try extending fully above your head.")
            else:
                scores["arm_extension"] = max(30, arm_ext * 0.5)
                feedback.append("Your arm is too bent. Fully extend for maximum power and height.")

            # Elbow angle (160-180 optimal for smash contact)
            if 155 <= elbow <= 180:
                scores["elbow_form"] = 90 + (elbow - 155) * 0.3
                feedback.append("Elbow lock is solid at contact point.")
            elif elbow > 120:
                scores["elbow_form"] = 60 + (elbow - 120)
                feedback.append("Slightly bent elbow. Try snapping your arm straight at impact.")
            else:
                scores["elbow_form"] = max(25, elbow * 0.5)
                feedback.append("Elbow is too bent — you're losing significant power.")

            # Wrist position (should be above shoulder)
            scores["wrist_height"] = 85 if wrist_above else 45
            if wrist_above:
                feedback.append("Good wrist height — shuttle contact is above shoulder level.")
            else:
                feedback.append("Contact point is too low. Reach higher and snap down on the shuttle.")

            # Hip rotation (20-60 degrees is good)
            if 20 <= hip_rot <= 60:
                scores["hip_rotation"] = 85 + hip_rot * 0.2
                feedback.append("Good hip rotation generating kinetic chain power.")
            else:
                scores["hip_rotation"] = 55
                feedback.append("Rotate your hips more during the jump for explosive power.")

            # Knee bend (for jump preparation)
            knee = min(body["right_knee_angle"], body["left_knee_angle"])
            if knee < 140:
                scores["knee_bend"] = 85
                feedback.append("Good knee bend for jump preparation.")
            else:
                scores["knee_bend"] = 60
                feedback.append("Bend your knees more before the jump to generate upward force.")

            # Hand grip
            if hands.get("hands_detected", 0) > 0:
                spread = hands["hands"][0]["finger_spread"]
                if spread < 30:
                    scores["grip"] = 90
                    feedback.append("Tight grip detected — good for smash power transfer.")
                else:
                    scores["grip"] = 65
                    feedback.append("Loosening grip during swing. Maintain firm grip through contact.")
            else:
                scores["grip"] = 50

        elif shot_type == "Serve":
            # Serve: low stance, wrist below waist, controlled position
            wrist_below = not body["right_wrist_above_shoulder"] and not body["left_wrist_above_shoulder"]
            knee = min(body["right_knee_angle"], body["left_knee_angle"])
            stance = body["stance_width"]
            shoulder = body["shoulder_width"]

            # Wrist position (should be low for legal serve)
            scores["wrist_position"] = 85 if wrist_below else 40
            if wrist_below:
                feedback.append("Correct wrist position below waist level for a legal serve.")
            else:
                feedback.append("Wrist is too high. Keep the racket head below waist level.")

            # Knee bend (low stance = better serve)
            if knee < 130:
                scores["stance_depth"] = 90
                feedback.append("Excellent low stance — perfect for a controlled serve.")
            elif knee < 150:
                scores["stance_depth"] = 75
                feedback.append("Good knee bend. Going lower improves serve consistency.")
            else:
                scores["stance_depth"] = 50
                feedback.append("Your stance is too upright. Bend your knees for better control.")

            # Stance width (shoulder-width is ideal)
            ratio = stance / shoulder if shoulder > 0 else 0
            if 0.8 <= ratio <= 1.3:
                scores["foot_spacing"] = 90
                feedback.append("Good foot positioning — shoulder-width apart for balance.")
            else:
                scores["foot_spacing"] = 60
                feedback.append("Adjust your foot spacing to about shoulder-width apart.")

            # Torso lean (slight forward lean is good)
            if body["torso_lean"] < shoulder * 0.3:
                scores["torso_control"] = 85
                feedback.append("Controlled torso position — minimal unnecessary movement.")
            else:
                scores["torso_control"] = 55
                feedback.append("Your torso is leaning too much. Stay more centered.")

            # Arm extension
            ext = max(body["right_arm_extension"], body["left_arm_extension"])
            scores["arm_control"] = 80 if ext < shoulder * 1.5 else 60
            feedback.append("Keep your racket arm controlled for an accurate serve trajectory.")

            # Hand
            scores["grip"] = 75
            if hands.get("hands_detected", 0) > 0:
                curl = hands["hands"][0]["index_curl"]
                if curl < 40:
                    scores["grip"] = 88
                    feedback.append("Relaxed grip allows for better serve touch and spin.")
                else:
                    scores["grip"] = 65
                    feedback.append("Tight grip detected. Relax your fingers for a softer serve.")

        elif shot_type == "Cross Drop":
            # Cross Drop: deception (shoulders square), racket preparation, light touch
            shoulder_sq = abs(body["right_shoulder_angle"] - body["left_shoulder_angle"])
            hip_rot = abs(body["right_hip_angle"] - body["left_hip_angle"])
            wrist_above = body["right_wrist_above_shoulder"] or body["left_wrist_above_shoulder"]

            # Shoulder squareness (deception indicator)
            if shoulder_sq < 20:
                scores["deception"] = 90
                feedback.append("Excellent shoulder squareness — opponent cannot read the shot direction.")
            elif shoulder_sq < 35:
                scores["deception"] = 72
                feedback.append("Good deception. Try keeping shoulders slightly more square to the net.")
            else:
                scores["deception"] = 45
                feedback.append("Your shoulders are rotated too much — opponent can read the cross direction early.")

            # Racket preparation height
            scores["preparation"] = 85 if wrist_above else 55
            if wrist_above:
                feedback.append("Good racket preparation height for drop shot deception.")
            else:
                feedback.append("Raise your racket earlier to sell the smash before dropping.")

            # Hip control (minimal rotation = better deception)
            if hip_rot < 25:
                scores["body_control"] = 88
                feedback.append("Stable hips maintain the deception throughout the stroke.")
            else:
                scores["body_control"] = 60
                feedback.append("Hip rotation reveals your intent. Keep hips stable until contact.")

            # Stance
            knee = min(body["right_knee_angle"], body["left_knee_angle"])
            scores["stance"] = 80 if knee < 150 else 55
            feedback.append("Maintain a balanced lunge stance for precise shuttle placement.")

            # Arm control (slight angle = finesse)
            elbow = min(body["right_elbow_angle"], body["left_elbow_angle"])
            if 100 <= elbow <= 150:
                scores["arm_control"] = 88
                feedback.append("Perfect elbow angle for a controlled cross-court drop.")
            else:
                scores["arm_control"] = 65
                feedback.append("Adjust your arm angle for more finesse on the drop shot.")

            # Hand (soft grip for touch)
            scores["grip"] = 78
            if hands.get("hands_detected", 0) > 0:
                spread = hands["hands"][0]["finger_spread"]
                if 15 < spread < 35:
                    scores["grip"] = 90
                    feedback.append("Ideal finger tension for a deceptive cross drop.")
                else:
                    scores["grip"] = 68

        elif shot_type == "Net Play":
            # Net Play: deep lunge, racket-side leg forward, arm extended forward
            knee = min(body["right_knee_angle"], body["left_knee_angle"])
            hip = min(body["right_hip_angle"], body["left_hip_angle"])
            stance = body["stance_width"]
            ext = max(body["right_arm_extension"], body["left_arm_extension"])

            # Lunge depth (knee angle < 100 is deep lunge)
            if knee < 100:
                scores["lunge_depth"] = 95
                feedback.append("Excellent deep lunge — maximizes court reach for net play.")
            elif knee < 130:
                scores["lunge_depth"] = 75
                feedback.append("Good lunge depth. Going deeper gives you more reach at the net.")
            else:
                scores["lunge_depth"] = 45
                feedback.append("Shallow lunge. Bend your front knee more for better net coverage.")

            # Hip angle (compression in lunge)
            if hip < 110:
                scores["hip_compression"] = 90
                feedback.append("Great hip compression — stable base for net kill or spin.")
            else:
                scores["hip_compression"] = 60
                feedback.append("Lower your hips in the lunge for a more stable net position.")

            # Arm reach (extended forward for net play)
            if ext > 160:
                scores["arm_reach"] = 90
                feedback.append("Full arm extension for maximum net reach.")
            elif ext > 130:
                scores["arm_reach"] = 75
                feedback.append("Good reach. Extend your arm further forward at the net.")
            else:
                scores["arm_reach"] = 50
                feedback.append("Arm is too close to body. Reach forward to take the shuttle early.")

            # Balance (torso lean should be minimal)
            shoulder_w = body["shoulder_width"]
            if body["torso_lean"] < shoulder_w * 0.25:
                scores["balance"] = 90
                feedback.append("Excellent balance — centered torso during the net lunge.")
            else:
                scores["balance"] = 60
                feedback.append("You're leaning too much. Engage your core for better balance.")

            # Stance width (wide = stable)
            ratio = stance / shoulder_w if shoulder_w > 0 else 0
            scores["stance"] = 85 if ratio > 1.0 else 55
            feedback.append("Ensure your racket-side leg leads the lunge toward the net.")

            # Hand (fingers spread for net kill sensitivity)
            scores["grip"] = 75
            if hands.get("hands_detected", 0) > 0:
                spread = hands["hands"][0]["finger_spread"]
                if spread > 25:
                    scores["grip"] = 88
                    feedback.append("Open grip allows for quick net kills and touch shots.")
                else:
                    scores["grip"] = 65
                    feedback.append("Fingers are too tight. Relax for better net touch sensitivity.")

        else:  # General Play
            # General: stance, readiness, balance
            stance = body["stance_width"]
            shoulder_w = body["shoulder_width"]
            knee = min(body["right_knee_angle"], body["left_knee_angle"])

            # Ready stance
            ratio = stance / shoulder_w if shoulder_w > 0 else 0
            if 1.0 <= ratio <= 1.5:
                scores["stance"] = 90
                feedback.append("Good ready stance — feet shoulder-width apart for quick movement.")
            else:
                scores["stance"] = 55
                feedback.append("Adjust stance width to 1.2x shoulder width for optimal readiness.")

            # Knee bend (athletic position)
            if knee < 150:
                scores["athletic_position"] = 88
                feedback.append("Good knee bend — you're in an athletic ready position.")
            else:
                scores["athletic_position"] = 55
                feedback.append("Bend your knees more. An upright stance slows explosive movements.")

            # Torso balance
            if body["torso_lean"] < shoulder_w * 0.2:
                scores["balance"] = 90
                feedback.append("Centered balance — ready to move in any direction.")
            else:
                scores["balance"] = 55
                feedback.append("Lean is off-center. Maintain a neutral spine for faster reactions.")

            # Arm readiness
            ext = max(body["right_arm_extension"], body["left_arm_extension"])
            if ext < shoulder_w * 2:
                scores["arm_readiness"] = 85
                feedback.append("Arms are in good position for quick racket preparation.")
            else:
                scores["arm_readiness"] = 60
                feedback.append("Arms are too extended. Keep them closer for faster racket work.")

            # Hand
            scores["grip"] = 75
            if hands.get("hands_detected", 0) > 0:
                curl = hands["hands"][0]["middle_curl"]
                if curl < 50:
                    scores["grip"] = 85
                    feedback.append("Relaxed grip in ready position — allows quick grip changes.")
                else:
                    scores["grip"] = 65
                    feedback.append("Grip looks tight. Relax between shots for better versatility.")

            # Footwork readiness
            scores["footwork"] = 80
            feedback.append("Stay on the balls of your feet for explosive split-step movement.")

        # Clamp all scores to 0-100
        scores = {k: max(0, min(100, v)) for k, v in scores.items()}

        # Calculate overall accuracy
        if scores:
            overall = round(sum(scores.values()) / len(scores))
        else:
            overall = 50

        # Determine verdict
        if overall >= 80:
            verdict = "Excellent"
        elif overall >= 65:
            verdict = "Good"
        elif overall >= 50:
            verdict = "Needs Work"
        else:
            verdict = "Poor"

        return {
            "stroke_type": shot_type,
            "verdict": verdict,
            "accuracy": overall,
            "feedback": " ".join(feedback),
            "metrics": scores,
            "body_angles": {
                "right_shoulder": body["right_shoulder_angle"],
                "left_shoulder": body["left_shoulder_angle"],
                "right_elbow": body["right_elbow_angle"],
                "left_elbow": body["left_elbow_angle"],
                "right_hip": body["right_hip_angle"],
                "left_hip": body["left_hip_angle"],
                "right_knee": body["right_knee_angle"],
                "left_knee": body["left_knee_angle"],
            },
            "hand_data": hands,
        }


def main():
    """Main entry point: receive image path + shot type, output JSON."""
    if len(sys.argv) < 3:
        print(json.dumps({"success": False, "error": "Usage: analysis_engine.py <image_path> <shot_type>"}))
        sys.exit(1)

    image_path = sys.argv[1]
    shot_type = sys.argv[2]

    valid_shots = ["Smash", "Serve", "Cross Drop", "Net Play", "General Play"]
    if shot_type not in valid_shots:
        shot_type = "General Play"

    if not os.path.exists(image_path):
        print(json.dumps({"success": False, "error": f"Image not found: {image_path}"}))
        sys.exit(1)

    try:
        analyzer = BadmintonAnalyzer()

        result = analyzer.analyze_pose(image_path)
        pose_lm = result[0]
        quality_score = result[4] if len(result) > 4 else 100
        quality_warnings = result[5] if len(result) > 5 else []

        if pose_lm is None:
            # No person detected OR full body not visible — fallback analysis
            ref_skeleton = analyzer.get_reference_skeleton(shot_type)
            # Use any quality_warnings returned from analyze_pose (includes full-body messages)
            final_warnings = quality_warnings if quality_warnings else [
                "No person detected. Ensure your full body is visible in the frame from head to toe."
            ]
            print(json.dumps({
                "success": True,
                "data": {
                    "stroke_type": shot_type,
                    "verdict": "Unreadable",
                    "accuracy": 0,
                    "feedback": final_warnings[0],
                    "metrics": {},
                    "body_angles": {},
                    "hand_data": {"hands_detected": 0},
                    "similarity_score": 0,
                    "sub_scores": {"footwork": 0, "posture": 0, "swing": 0},
                    "reference_skeleton": ref_skeleton,
                    "detected_skeleton": None,
                    "quality_score": quality_score,
                    "quality_warnings": final_warnings,
                    "detected_shot_type": shot_type,
                    "detection_confidence": 0,
                    "shot_type_scores": {},
                    "all_similarities": {},
                }
            }))
            sys.exit(0)

        img_w, img_h = result[1], result[2]
        hand_landmarks = result[3]

        body_metrics = analyzer.extract_body_metrics(pose_lm, img_w, img_h)
        hand_metrics = analyzer.extract_hand_metrics(hand_landmarks, img_w, img_h)

        # AUTO-DETECT: Determine the most likely shot type from the pose
        detected_type, detection_confidence, type_scores = analyzer.auto_detect_shot_type(body_metrics, hand_metrics)

        # Score against the DETECTED shot type (primary analysis)
        analysis = analyzer.score_shot(detected_type, body_metrics, hand_metrics)

        # Also calculate similarity against ALL references for comparison
        user_norm = analyzer.normalize_landmarks(pose_lm, img_w, img_h)
        all_similarities = {}
        for ref_name in analyzer.REFERENCE_POSES:
            ref_pose = analyzer.REFERENCE_POSES[ref_name]["landmarks"]
            sim, _ = analyzer.calculate_similarity(user_norm, ref_pose)
            all_similarities[ref_name] = sim

        # The primary similarity is against the detected type
        similarity = all_similarities.get(detected_type, 0)

        # Extract skeletons for frontend rendering
        detected_skeleton = analyzer.extract_detected_skeleton(pose_lm, img_w, img_h)
        reference_skeleton = analyzer.get_reference_skeleton(detected_type)

        # Compute real sub-scores from metrics
        scores = analysis.get("metrics", {})
        
        # Footwork: based on stance width, knee angles, balance
        footwork_scores = []
        if "stance" in scores: footwork_scores.append(scores["stance"])
        if "athletic_position" in scores: footwork_scores.append(scores["athletic_position"])
        if "foot_spacing" in scores: footwork_scores.append(scores["foot_spacing"])
        if "footwork" in scores: footwork_scores.append(scores["footwork"])
        if "lunge_depth" in scores: footwork_scores.append(scores["lunge_depth"])
        footwork_sub = round(sum(footwork_scores) / len(footwork_scores)) if footwork_scores else analysis["accuracy"]

        # Posture: based on torso, balance, hip
        posture_scores = []
        if "torso_control" in scores: posture_scores.append(scores["torso_control"])
        if "balance" in scores: posture_scores.append(scores["balance"])
        if "hip_rotation" in scores: posture_scores.append(scores["hip_rotation"])
        if "hip_compression" in scores: posture_scores.append(scores["hip_compression"])
        if "body_control" in scores: posture_scores.append(scores["body_control"])
        posture_sub = round(sum(posture_scores) / len(posture_scores)) if posture_scores else analysis["accuracy"]

        # Swing: based on arm, elbow, wrist, grip
        swing_scores = []
        if "arm_extension" in scores: swing_scores.append(scores["arm_extension"])
        if "arm_reach" in scores: swing_scores.append(scores["arm_reach"])
        if "arm_readiness" in scores: swing_scores.append(scores["arm_readiness"])
        if "elbow_form" in scores: swing_scores.append(scores["elbow_form"])
        if "wrist_height" in scores: swing_scores.append(scores["wrist_height"])
        if "wrist_position" in scores: swing_scores.append(scores["wrist_position"])
        if "grip" in scores: swing_scores.append(scores["grip"])
        swing_sub = round(sum(swing_scores) / len(swing_scores)) if swing_scores else analysis["accuracy"]

        # Apply quality penalty — low quality images reduce confidence in scores
        quality_penalty = 0
        if quality_score < 50:
            quality_penalty = 15
        elif quality_score < 70:
            quality_penalty = 8

        # Adjust final accuracy with quality penalty
        adjusted_accuracy = max(0, analysis["accuracy"] - quality_penalty)

        # Recalculate sub-scores with quality penalty
        footwork_sub = max(0, footwork_sub - quality_penalty)
        posture_sub = max(0, posture_sub - quality_penalty)
        swing_sub = max(0, swing_sub - quality_penalty)

        analysis["accuracy"] = adjusted_accuracy
        analysis["verdict"] = (
            "Excellent" if adjusted_accuracy >= 80 else
            "Good" if adjusted_accuracy >= 65 else
            "Needs Work" if adjusted_accuracy >= 40 else
            "Poor"
        ) if adjusted_accuracy > 0 else "Unreadable"

        analysis["similarity_score"] = similarity
        analysis["sub_scores"] = {
            "footwork": footwork_sub,
            "posture": posture_sub,
            "swing": swing_sub,
        }
        analysis["reference_skeleton"] = reference_skeleton
        analysis["detected_skeleton"] = detected_skeleton
        analysis["quality_score"] = quality_score
        analysis["quality_warnings"] = quality_warnings
        analysis["detected_shot_type"] = detected_type
        analysis["detection_confidence"] = detection_confidence
        analysis["shot_type_scores"] = type_scores
        analysis["all_similarities"] = all_similarities

        print(json.dumps({"success": True, "data": analysis}))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
