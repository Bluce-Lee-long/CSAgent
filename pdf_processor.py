import PyPDF2
import re
from typing import List, Dict
from config import Config

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def extract_text(self) -> str:
        """提取PDF文档的文本内容"""
        text = ""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"📄 PDF文档信息: {len(pdf_reader.pages)} 页")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n=== 第{page_num}页 ===\n{page_text}\n"
                        print(f"✅ 第{page_num}页提取成功，长度: {len(page_text)} 字符")
                    else:
                        print(f"⚠️ 第{page_num}页内容为空")
                        
        except Exception as e:
            print(f"❌ PDF处理错误: {e}")
            return ""
        return text
    
    def clean_text(self, text: str) -> str:
        """清理文本内容（保留换行，便于按小节/标题切分）"""
        print("🧹 开始清理文本...")

        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 移除页面标记
        text = re.sub(r'\n?=== 第\d+页 ===\n?', '\n', text)

        # 行内多余空白收缩，但保留换行
        text = re.sub(r'[ \t]+', ' ', text)

        # 移除两端空白的空行，并收敛连续空行为单个空行
        # 先逐行strip，再重新拼接
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        cleaned_text = text.strip('\n ')
        print(f"✅ 文本清理完成，总长度: {len(cleaned_text)} 字符")
        return cleaned_text

    def _is_heading(self, line: str) -> bool:
        """基于启发式规则判断一行是否为标题/小节。
        适配常见中文与数字编号标题：如“1 概述”、“1.2 目标”、“一、背景”、“（一）现状”、“第3章 方法”等。
        """
        if not line:
            return False

        candidate = line.strip()
        if len(candidate) == 0:
            return False

        # 短行更可能是标题
        is_relatively_short = len(candidate) <= 30

        patterns = [
            r'^\d{1,3}(?:[\.|．]\d{1,3}){0,3}[\s、).)]+',            # 1 / 1.1 / 1.1.1
            r'^[（\(]?\d{1,3}[）\)]',                                 # （1）
            r'^[一二三四五六七八九十百千万]+、',                             # 一、 二、 …
            r'^[（\(][一二三四五六七八九十百千万]+[）\)]',                 # （一）
            r'^第[一二三四五六七八九十百千万0-9]+[章节部分卷]',               # 第三章 / 第1节
        ]

        # 以冒号/：结尾的短行也多为标题
        looks_like_title_suffix = is_relatively_short and candidate.endswith((':', '：'))

        for p in patterns:
            if re.match(p, candidate):
                return True

        # 无句末终止符号且较短，且不以句号结束，可能为标题
        no_sentence_ending = not re.search(r'[。！？.!?；;]$', candidate)
        return is_relatively_short and (looks_like_title_suffix or no_sentence_ending)

    def _split_into_sections(self, text: str) -> List[Dict]:
        """按标题/小节拆分文本，返回 [{title, text}]。若未检测到标题，则返回单节。"""
        lines = [line for line in text.split('\n') if line is not None]
        sections: List[Dict] = []

        current_title = '正文'
        current_lines: List[str] = []
        detected_any_heading = False

        for line in lines:
            if self._is_heading(line):
                # 刷新上一节
                if current_lines:
                    sections.append({'title': current_title, 'text': '\n'.join(current_lines).strip()})
                current_title = line.strip()
                current_lines = []
                detected_any_heading = True
            else:
                current_lines.append(line)

        # 收尾
        if current_lines:
            sections.append({'title': current_title, 'text': '\n'.join(current_lines).strip()})

        if not detected_any_heading:
            return [{'title': '全文', 'text': text.strip()}]

        return sections

    def _chunk_section(self, section_text: str, section_title: str, section_index: int) -> List[Dict]:
        """在单个小节内按句子+长度进行分块，并保留重叠。"""
        # 句子切分，保留终止符
        parts = re.split(r'([。！？!?；;])', section_text)
        sentences: List[str] = []
        for i in range(0, len(parts), 2):
            if i < len(parts):
                sentence = parts[i].strip()
                if i + 1 < len(parts):
                    sentence += parts[i + 1]
                if sentence:
                    sentences.append(sentence)

        # 如果未能按句子切出，则回退为按行
        if not sentences:
            sentences = [s for s in section_text.split('\n') if s.strip()]

        chunks: List[Dict] = []
        current_chunk = ''
        chunk_id = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'chunk_id': chunk_id,
                    'length': len(current_chunk),
                    'section_title': section_title,
                    'section_index': section_index,
                })
                chunk_id += 1

                # 重叠
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + sentence
            else:
                current_chunk += sentence

        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'chunk_id': chunk_id,
                'length': len(current_chunk),
                'section_title': section_title,
                'section_index': section_index,
            })

        return chunks
    
    def split_into_chunks(self, text: str) -> List[Dict]:
        """优先按标题/小节切分，再在小节内按长度合并，保留重叠。"""
        print("✂️ 开始分割文本块（结构化优先）...")

        sections = self._split_into_sections(text)
        all_chunks: List[Dict] = []

        for idx, sec in enumerate(sections):
            section_chunks = self._chunk_section(sec['text'], sec['title'], idx)
            all_chunks.extend(section_chunks)

        print(f"✅ 文本分割完成，共生成 {len(all_chunks)} 个文本块（{len(sections)} 个小节）")
        return all_chunks
    
    def process_document(self) -> List[Dict]:
        """处理整个文档"""
        print("🔄 开始处理PDF文档...")
        print(f"📁 文档路径: {self.pdf_path}")
        
        raw_text = self.extract_text()
        print(raw_text)
        
        if not raw_text:
            print("❌ 无法提取PDF内容")
            return []
        
        print(f"📊 原始文本长度: {len(raw_text)} 字符")
        
        cleaned_text = self.clean_text(raw_text)
        
        if not cleaned_text:
            print("❌ 文本清理后为空")
            return []
        
        chunks = self.split_into_chunks(cleaned_text)
        
        # 显示前几个块的预览
        print("\n📋 文本块预览:")
        for i, chunk in enumerate(chunks[:3]):
            preview = chunk['text'][:100] + "..." if len(chunk['text']) > 100 else chunk['text']
            sec = f" | 小节: {chunk.get('section_title', 'N/A')}"
            print(f"  块{i+1}{sec}: {preview}")
        
        if len(chunks) > 3:
            print(f"  ... 还有 {len(chunks) - 3} 个文本块")
        
        print(f"\n✅ 文档处理完成，共生成 {len(chunks)} 个文本块")
        return chunks

if __name__ == "__main__":
    processor = PDFProcessor(Config.PDF_PATH)
    chunks = processor.process_document()
    print(f"\n🎯 最终结果: 共 {len(chunks)} 个文本块")
    
    # 显示统计信息
    if chunks:
        total_length = sum(chunk['length'] for chunk in chunks)
        avg_length = total_length / len(chunks)
        print(f"📊 统计信息:")
        print(f"  总字符数: {total_length}")
        print(f"  平均块长度: {avg_length:.1f} 字符")
        print(f"  最长块: {max(chunk['length'] for chunk in chunks)} 字符")
        print(f"  最短块: {min(chunk['length'] for chunk in chunks)} 字符")
