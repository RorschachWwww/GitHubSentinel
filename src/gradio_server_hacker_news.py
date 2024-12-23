import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from hacker_news_client import HackerNewsClient  # 导入用于Hacker News API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hackernews_client = HackerNewsClient()  # 创建HackerNews客户端实例
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)


def generate_report(data_source, repo=None, days=None):
    if data_source == "GitHub":
        if repo is None or days is None:
            return "请选择GitHub项目和报告周期", None
        # 调用GitHub数据处理逻辑
        raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
        report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径
        return report, report_file_path  # 返回报告内容和报告文件路径

    elif data_source == "Hacker News":
        # 调用Hacker News数据处理逻辑
        raw_file_path = hackernews_client.export_daily_progress()  # 导出Hacker News原始数据
        report, report_file_path = report_generator.generate_daily_report(raw_file_path)  # 生成Hacker News相关报告
        return report, report_file_path


# 创建Gradio界面
data_source_dropdown = gr.Dropdown(
    choices=["GitHub", "Hacker News"],
    label="选择数据来源",
    info="选择数据来源：GitHub或Hacker News"
)

github_repo_dropdown = gr.Dropdown(
    subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
)

days_slider = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期",
                        info="生成项目过去一段时间进展，单位：天")

# 在GitHub选择时显示订阅项目和报告周期，Hacker News选择时不显示这些
inputs = [
    data_source_dropdown,
    github_repo_dropdown,
    days_slider
]

outputs = [gr.Markdown(), gr.File(label="下载报告")]


def toggle_inputs(data_source):
    # 根据数据来源选择来决定显示哪些输入组件
    if data_source == "Hacker News":
        return gr.update(visible=False), gr.update(visible=False)  # 隐藏GitHub相关输入
    else:
        return gr.update(visible=True), gr.update(visible = True)  # 显示GitHub相关输入


# 使用gr.Blocks创建界面
with gr.Blocks() as demo:
    # 创建输入输出组件
    data_source_dropdown.change(toggle_inputs, inputs=data_source_dropdown, outputs=[github_repo_dropdown, days_slider])
    gr.Interface(
        fn=generate_report,  # 指定界面调用的函数
        title="GitHubSentinel",  # 设置界面标题
        inputs=inputs,
        outputs=outputs
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="127.0.0.1")  # 启动界面并设置为公共可访问
