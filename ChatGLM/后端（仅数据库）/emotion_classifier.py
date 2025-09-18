import paddle
import paddle.nn.functional as F
from paddlenlp.transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from collections import Counter
import re

class EnhancedPaddleEmotionClassifier:
    def __init__(self):
        # 使用更适合情感分析的大型预训练模型
        self.model_name = "ernie-3.0-xbase-zh"  # 更大的模型，效果更好
        
        # 初始化tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # 更细粒度的情绪标签（可根据实际需求调整）
        self.emotion_labels = ['高兴', '悲伤', '愤怒', '恐惧', '惊讶', '厌恶', '中性', '期待', '信任']
        
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_classes=len(self.emotion_labels)
        )
        
        # 加载预训练权重（如果有的话）
        # self.model.set_state_dict(paddle.load('path_to_trained_model'))
        
        # 设置模型为评估模式
        self.model.eval()
        
        # 情感关键词词典（用于后处理增强）
        self.emotion_keywords = {
            '高兴': ['开心', '快乐', '高兴', '愉快', '幸福', '笑容', '美好', '喜悦', '欢乐', '兴奋', '激动'],
            '悲伤': ['伤心', '难过', '悲伤', '痛苦', '哭泣', '失落', '绝望', '沮丧', '忧郁', '悲痛', '泪'],
            '愤怒': ['生气', '愤怒', '气愤', '怒火', '讨厌', '恨', '烦躁', '恼火', '愤怒', '暴躁', '发火'],
            '恐惧': ['害怕', '恐惧', '惊吓', '恐怖', '惊慌', '担心', '焦虑', '恐慌', '畏惧', '不安', '紧张'],
            '惊讶': ['惊讶', '惊奇', '意外', '震惊', '居然', '竟然', '吃惊', '诧异', '意想不到', '出乎意料'],
            '厌恶': ['恶心', '厌恶', '讨厌', '反感', '嫌弃', '憎恶', '鄙视', '失望', '厌恶', '唾弃'],
            '中性': ['一般', '普通', '正常', '平常', '日常', '普通', '寻常', '平淡'],
            '期待': ['期待', '希望', '盼望', '渴望', '期望', '期盼', '憧憬', '向往', '等待'],
            '信任': ['信任', '相信', '信赖', '可靠', '诚信', '诚实', '真诚', '信赖', '依靠']
        }
        
        # 否定词列表（用于检测否定表达）
        self.negation_words = ['不', '没', '无', '非', '未', '莫', '勿', '别', '没有', '不会', '不能']
    
    def preprocess_text(self, text):
        """文本预处理"""
        # 去除特殊字符和多余空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 处理否定词
        words = text.split()
        for i, word in enumerate(words):
            if word in self.negation_words and i + 1 < len(words):
                words[i + 1] = 'NOT_' + words[i + 1]
        
        return ' '.join(words)
    
    def detect_emotion_keywords(self, text):
        """检测文本中的情感关键词"""
        text_lower = text.lower()
        keyword_counts = {label: 0 for label in self.emotion_labels}
        
        # 检查情感词
        for label, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                # 简单匹配关键词
                if keyword in text_lower:
                    keyword_counts[label] += 1
        
        return keyword_counts
    
    def keyword_enhancement(self, text, probabilities):
        """基于情感关键词增强预测结果"""
        # 检测文本中的情感关键词
        keyword_counts = self.detect_emotion_keywords(text)
        
        # 计算总的关键词数量
        total_keywords = sum(keyword_counts.values())
        
        # 如果检测到情感关键词，调整概率
        if total_keywords > 0:
            enhanced_probs = probabilities.copy()
            
            # 为每个检测到关键词的情感类别增加权重
            for label, count in keyword_counts.items():
                if count > 0:
                    # 根据关键词数量增加权重
                    enhancement = 0.15 * (count / total_keywords)
                    enhanced_probs[label] = min(1.0, enhanced_probs[label] + enhancement)
            
            # 重新归一化概率
            total = sum(enhanced_probs.values())
            enhanced_probs = {k: v/total for k, v in enhanced_probs.items()}
            
            return enhanced_probs
        
        return probabilities
    
    def predict_emotion(self, text, use_enhancement=True):
        """预测情绪"""
        # 文本预处理
        processed_text = self.preprocess_text(text)
        
        # 编码文本
        inputs = self.tokenizer(
            processed_text,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pd"
        )
        
        # 预测
        with paddle.no_grad():
            logits = self.model(**inputs)
        
        # 计算概率
        probabilities = F.softmax(logits, axis=1)
        predicted_idx = paddle.argmax(probabilities, axis=1).item()
        
        # 转换为概率字典
        prob_dict = {label: probabilities[0][i].item() 
                    for i, label in enumerate(self.emotion_labels)}
        
        # 应用后处理增强
        if use_enhancement:
            prob_dict = self.keyword_enhancement(text, prob_dict)
            predicted_idx = np.argmax(list(prob_dict.values()))
        
        return {
            'emotion': self.emotion_labels[predicted_idx],
            'confidence': list(prob_dict.values())[predicted_idx],
            'probabilities': prob_dict,
            'text': text
        }
    
    def predict_batch(self, texts, batch_size=8):
        """批量预测，提高效率"""
        results = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_results = [self.predict_emotion(text) for text in batch_texts]
            results.extend(batch_results)
        return results

# 使用示例和评估
if __name__ == "__main__":
    # 初始化分类器
    classifier = EnhancedPaddleEmotionClassifier()
    
    # 测试文本
    test_texts = [
        "哈吉米南北绿豆，椰果奶龙",
        "我真的很难过，失去了重要的人。",
        "这太让人生气了，怎么能这样！",
        "有点害怕一个人走夜路。",
        "我一点也不高兴，我很生气",
        "我非常开心能够见到你，这真是令人兴奋的事情！",
        "不是很喜欢这个电影，有点失望",
        "超级害怕蜘蛛，看到就浑身发抖"
    ]
    
    print("情绪识别测试结果：")
    print("=" * 50)
    
    for text in test_texts:
        result = classifier.predict_emotion(text)
        print(f"文本: {text}")
        print(f"预测情绪: {result['emotion']} (置信度: {result['confidence']:.4f})")
        
        # 显示所有情绪概率
        print("情绪概率分布:")
        for emotion, prob in sorted(result['probabilities'].items(), 
                                  key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {emotion}: {prob:.4f}")
        print("-" * 30)