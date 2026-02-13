def calculate_stress(gsr_now, gsr_base, hr_now, hr_base, spo2_now=None, spo2_base=98):
    """
    Medical-based stress scoring with baseline fallback
    Output: 0 ~ 100
    """

    if gsr_now is None or hr_now is None:
        return 30

    # ---------- GSR ----------
    gsr_delta = gsr_now - gsr_base
    gsr_ratio = abs(gsr_delta) / gsr_base

    if gsr_ratio < 0.01:
        gsr_score = 20
    elif gsr_ratio < 0.015:
        gsr_score = 30
    elif gsr_ratio < 0.02:
        gsr_score = 40
    elif gsr_ratio < 0.025:
        gsr_score = 50
    elif gsr_ratio < 0.03:
        gsr_score = 65
    else:
        gsr_score = 85

    # ---------- HR ----------
    hr_delta = hr_now - hr_base
    hr_ratio = hr_delta / hr_base

    if hr_ratio < -0.05:
        hr_score = 15
    elif hr_ratio < -0.03:
        hr_score = 20
    elif abs(hr_ratio) < 0.02:
        hr_score = 25
    elif hr_ratio < 0.035:
        hr_score = 35
    elif hr_ratio < 0.05:
        hr_score = 45
    elif hr_ratio < 0.075:
        hr_score = 60
    elif hr_ratio < 0.10:
        hr_score = 70
    else:
        hr_score = 90

    final_score = 0.6 * gsr_score + 0.4 * hr_score

    # 🔴 ---------- SpO₂ 보정 ----------
    if spo2_now is not None:
        spo2_drop = spo2_base - spo2_now

        if spo2_now <= 92:
            final_score += 25
        elif spo2_now <= 94:
            final_score += 15
        elif spo2_drop >= 1.5:
            final_score += 10
        elif spo2_drop >= 0.8:
            final_score += 5

    # ---------- Minimum & Clamp ----------
    if final_score < 25:
        final_score = 25

    if final_score > 100:
        final_score = 100

    return int(round(final_score))