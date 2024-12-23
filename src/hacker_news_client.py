import requests
from bs4 import BeautifulSoup
from logger import LOG  # 导入日志模块
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作

class HackerNewsClient:

    def fetch_hackernews_top_stories(self):
        url = 'https://news.ycombinator.com/'
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        return top_stories

    def export_daily_progress(self):
        repo = "hacker_news"
        LOG.debug(f"[准备导出项目进度]：{repo}")
        timestamp = datetime.now().isoformat().replace(':', '-')  # 获取今天的日期
        stories = self.fetch_hackernews_top_stories()  # 获取今天的更新数据

        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建存储路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在

        file_path = os.path.join(repo_dir, f'{timestamp}.md')  # 构建文件路径
        LOG.debug(f"[开始导出项目进度]：{repo}")
        with open(file_path, 'w') as file:
            file.write(f"# Top topics for {repo} ({timestamp})\n\n")
            file.write("\n## Top topics Today\n")
            for idx, story in enumerate(stories, start=1):
                file.write(f"{idx}. {story['title']}\n")
                file.write(f"   Link: {story['link']}\n")

        LOG.info(f"[{repo}]每日top话题文件生成： {file_path}")  # 记录日志
        return file_path