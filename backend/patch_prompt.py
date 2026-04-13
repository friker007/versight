import os

model_path = r"d:\versight\versight_with_backend\versight\backend\model.py"
with open(model_path, "r", encoding="utf-8") as f:
    code = f.read()

old_prompt = """You are an elite logical forensics AI. I am providing you with up to 4 uniformly sampled frames from a single video.
Your job is to act as a deepfake fact-checker by analyzing the CONTEXT and PHYSICS of the scene.
Are there impossible physics? Are there public figures doing/saying something historically impossible or extremely out of character? 
Is the lighting or interaction between subjects fundamentally illogical?

Respond STRICTLY with a JSON object containing exactly two keys:
1. "logical_reasoning": A 2-3 sentence paragraph explaining your logical analysis and fact-checking.
2. "anomaly_score": An integer from 0 to 100, where 100 heavily implies the context is an AI-generated or manipulated deepfake, and 0 implies it is logically coherent and perfectly realistic."""

new_prompt = """You are an elite visual forensics AI. I am providing you with up to 4 uniformly sampled frames from a video.
Your job is to act as a deepfake visual fact-checker. You must heavily scrutinize the CONTEXT, PHYSICS, and UNCANNY VISUALS of the scene.
Are the facial features too perfect, shiny, or unnaturally smoothed? Do the eyes/teeth look synthetic? Does the lighting on the subject truly match the background? Are the facial expressions slightly robotic, "uncanny", or AI-generated? Even if the scene is mundane (like a person sitting and talking), aggressively penalize any AI-generation or deepfake traits you observe.

Respond STRICTLY with a JSON object containing exactly two keys:
1. "logical_reasoning": A 2-3 sentence paragraph explaining your visual analysis and why it looks natural or synthetic.
2. "anomaly_score": An integer from 0 to 100, where 100 heavily implies the face/context is AI-generated, synthetic, or manipulated, and 0 implies it is a 100% natural, unaltered physical camera recording."""

if old_prompt in code:
    code = code.replace(old_prompt, new_prompt)
    with open(model_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Prompt patched beautifully.")
else:
    print("Could not find old prompt.")
