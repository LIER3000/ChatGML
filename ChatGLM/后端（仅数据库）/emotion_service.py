# emotion_service.py
from flask import Flask, request, jsonify
import json
import os
import sys

# 导入情感分析模型类
from emotion_classifier import EnhancedPaddleEmotionClassifier

# 屏蔽 transformers 编译信息，因为这个服务只使用PaddleNLP
os.environ["TRANSFORMERS_NO_COMPILATION"] = "1"

app = Flask(__name__)
emotion_classifier = None

@app.route('/predict_emotion', methods=['POST'])
def predict_emotion_endpoint():
    """
    处理情感分析请求的API端点。
    """
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({'error': '请在请求体中提供"text"字段'}), 400
        
        if emotion_classifier is None:
            return jsonify({'error': '情感分析模型未加载'}), 503

        result = emotion_classifier.predict_emotion(text)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'处理请求时发生错误: {e}'}), 500

def load_model():
    """
    加载情感分析模型。
    """
    global emotion_classifier
    try:
        emotion_classifier = EnhancedPaddleEmotionClassifier()
        print("✅ 情感分析服务模型初始化成功。")
    except Exception as e:
        print(f"❌ 情感分析模型初始化失败: {e}")
        sys.exit(1) # 如果模型加载失败，则退出服务

if __name__ == '__main__':
    print("==== 正在启动情感分析服务 ====")
    load_model()
    app.run(host='127.0.0.1', port=5001) # 在一个不冲突的端口上运行