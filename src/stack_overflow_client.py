import requests
from logger import LOG  # 导入日志模块
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os
class StackOverflowClient:
    def __init__(self):
        self.url = "https://api.stackexchange.com/2.3/questions"

    def fetch_top_issue_list(self):
        params = {
            "order": "desc",  # 按降序排序
            "sort": "votes",  # 按活跃度排序
            "site": "stackoverflow",  # 数据来源是 Stack Overflow
            "tagged": "python"
        }

        # 发送请求
        response = requests.get(self.url, params=params)
        issues = []

        if response.status_code == 200:
            data = response.json()
            questions = data.get("items", [])
            for question in questions[:10]:  # 获取前 10 条数据
                issues.append({'title':question['title'], 'link':question['link'], 'score':question['score']})
                print(f"标题: {question['title']}")
                print(f"链接: {question['link']}")
                print(f"投票数: {question['score']}\n")
            return issues
        else:
            print("请求失败:", response.status_code)

    def export_daily_issues(self):
        LOG.debug("准备导出issues")
        today = datetime.now().date().isoformat()  # 获取今天的日期
        issues = self.fetch_top_issue_list()  # 获取今天的更新数据

        issue_dir = os.path.join('stack_overflow', 'issues')  # 构建存储路径
        os.makedirs(issue_dir, exist_ok=True)  # 确保目录存在

        file_path = os.path.join(issue_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Top issues in stack overflow of python on ({today})\n\n")
            for issue in issues:  # 写入今天关闭的问题
                file.write(f"- title:{issue['title']}\n")
                file.write(f"- link:{issue['link']}\n")
                file.write(f"- score:{issue['score']}\n\n")

        LOG.info(f"stackoverflow python 每日issue top list生成： {file_path}")  # 记录日志
        return file_path

if __name__ == '__main__':
    client = StackOverflowClient()
    client.export_daily_issues()