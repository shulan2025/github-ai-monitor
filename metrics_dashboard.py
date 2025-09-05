#!/usr/bin/env python3
"""
增强指标仪表板生成器
生成HTML格式的AI项目指标分析报告
"""

import os
import json
from datetime import datetime
from cloudflare import Cloudflare
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Cloudflare配置
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
D1_DATABASE_ID = os.environ.get('D1_DATABASE_ID')

cloudflare_client = Cloudflare(api_token=CLOUDFLARE_API_TOKEN)

def fetch_dashboard_data():
    """获取仪表板数据"""
    try:
        queries = {
            'overview': """
                SELECT 
                    COUNT(*) as total_projects,
                    AVG(enhanced_score) as avg_score,
                    MAX(enhanced_score) as max_score,
                    MIN(enhanced_score) as min_score,
                    AVG(stars) as avg_stars,
                    SUM(contributors_count) as total_contributors
                FROM repos
            """,
            
            'top_projects': """
                SELECT 
                    name, owner, enhanced_score, stars, forks, 
                    ai_maturity_level, community_health, innovation_level, commercial_potential
                FROM repos 
                ORDER BY enhanced_score DESC 
                LIMIT 20
            """,
            
            'ai_maturity_distribution': """
                SELECT 
                    ai_maturity_level, 
                    COUNT(*) as count,
                    AVG(enhanced_score) as avg_score
                FROM repos 
                GROUP BY ai_maturity_level
            """,
            
            'innovation_analysis': """
                SELECT 
                    innovation_level,
                    COUNT(*) as count,
                    AVG(cutting_edge_score) as avg_cutting_edge,
                    AVG(research_quality_score) as avg_research_quality
                FROM repos 
                GROUP BY innovation_level
            """,
            
            'commercial_potential': """
                SELECT 
                    commercial_potential,
                    COUNT(*) as count,
                    AVG(enterprise_adoption_score) as avg_enterprise_score
                FROM repos 
                GROUP BY commercial_potential
            """,
            
            'technology_stack': """
                SELECT 
                    primary_language,
                    COUNT(*) as count,
                    AVG(enhanced_score) as avg_score
                FROM repos 
                WHERE primary_language != 'Unknown'
                GROUP BY primary_language 
                ORDER BY count DESC 
                LIMIT 10
            """,
            
            'ai_frameworks': """
                SELECT 
                    ai_framework,
                    COUNT(*) as count,
                    AVG(enhanced_score) as avg_score
                FROM repos 
                WHERE ai_framework != 'unknown'
                GROUP BY ai_framework 
                ORDER BY count DESC
            """,
            
            'community_health': """
                SELECT 
                    community_health,
                    COUNT(*) as count,
                    AVG(contributors_count) as avg_contributors,
                    AVG(commit_frequency_score) as avg_commit_frequency
                FROM repos 
                GROUP BY community_health
            """,
            
            'trending_projects': """
                SELECT 
                    name, owner, enhanced_score, stars, 
                    cutting_edge_score, innovation_level,
                    last_commit_date
                FROM repos 
                WHERE cutting_edge_score > 10
                ORDER BY cutting_edge_score DESC, enhanced_score DESC
                LIMIT 15
            """
        }
        
        dashboard_data = {}
        
        for query_name, sql in queries.items():
            try:
                response = cloudflare_client.d1.database.query(
                    database_id=D1_DATABASE_ID,
                    account_id=CLOUDFLARE_ACCOUNT_ID,
                    sql=sql
                )
                
                if response.success and response.result:
                    dashboard_data[query_name] = response.result[0].results
                else:
                    dashboard_data[query_name] = []
                    
            except Exception as e:
                print(f"❌ 查询 {query_name} 失败: {e}")
                dashboard_data[query_name] = []
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ 获取仪表板数据失败: {e}")
        return {}

def generate_html_dashboard(data):
    """生成HTML仪表板"""
    
    # 获取概览数据
    overview = data.get('overview', [{}])[0] if data.get('overview') else {}
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub AI项目增强指标仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .metric-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .table-container {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
        }}
        
        .badge-production {{ background: #28a745; }}
        .badge-mature {{ background: #17a2b8; }}
        .badge-developing {{ background: #ffc107; color: #333; }}
        .badge-experimental {{ background: #6c757d; }}
        
        .badge-excellent {{ background: #28a745; }}
        .badge-good {{ background: #17a2b8; }}
        .badge-fair {{ background: #ffc107; color: #333; }}
        .badge-poor {{ background: #dc3545; }}
        
        .badge-cutting-edge {{ background: #e83e8c; }}
        .badge-high {{ background: #fd7e14; }}
        .badge-medium {{ background: #6f42c1; }}
        .badge-low {{ background: #6c757d; }}
        
        .badge-very-high {{ background: #28a745; }}
        .badge-medium {{ background: #ffc107; color: #333; }}
        
        .score {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .score-excellent {{ color: #28a745; }}
        .score-good {{ color: #17a2b8; }}
        .score-fair {{ color: #ffc107; }}
        .score-poor {{ color: #dc3545; }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .overview {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🚀 GitHub AI项目增强指标仪表板</h1>
            <p>基于100分制综合评分的AI项目价值分析</p>
            <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="overview">
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_projects', 0)}</div>
                <div class="metric-label">总项目数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('avg_score', 0):.1f}</div>
                <div class="metric-label">平均评分</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('max_score', 0):.0f}</div>
                <div class="metric-label">最高评分</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('avg_stars', 0):.0f}</div>
                <div class="metric-label">平均星标</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_contributors', 0):.0f}</div>
                <div class="metric-label">总贡献者</div>
            </div>
        </div>
        
        <div class="content">
            <!-- 顶级项目排行榜 -->
            <div class="section">
                <h2>🏆 顶级AI项目排行榜 (Top 20)</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>项目</th>
                                <th>综合评分</th>
                                <th>星标</th>
                                <th>分叉</th>
                                <th>AI成熟度</th>
                                <th>社区健康</th>
                                <th>创新水平</th>
                                <th>商业潜力</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # 添加顶级项目表格
    top_projects = data.get('top_projects', [])
    for i, project in enumerate(top_projects[:20], 1):
        score_class = "score-excellent" if project.get('enhanced_score', 0) >= 80 else \
                     "score-good" if project.get('enhanced_score', 0) >= 60 else \
                     "score-fair" if project.get('enhanced_score', 0) >= 40 else "score-poor"
        
        html_content += f"""
                            <tr>
                                <td><strong>#{i}</strong></td>
                                <td>
                                    <strong>{project.get('owner', '')}/{project.get('name', '')}</strong>
                                </td>
                                <td class="{score_class}">{project.get('enhanced_score', 0):.1f}</td>
                                <td>{project.get('stars', 0):,}</td>
                                <td>{project.get('forks', 0):,}</td>
                                <td><span class="badge badge-{project.get('ai_maturity_level', 'unknown')}">{project.get('ai_maturity_level', 'Unknown')}</span></td>
                                <td><span class="badge badge-{project.get('community_health', 'unknown')}">{project.get('community_health', 'Unknown')}</span></td>
                                <td><span class="badge badge-{project.get('innovation_level', 'unknown')}">{project.get('innovation_level', 'Unknown')}</span></td>
                                <td><span class="badge badge-{project.get('commercial_potential', 'unknown')}">{project.get('commercial_potential', 'Unknown')}</span></td>
                            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- 图表分析 -->
            <div class="section">
                <h2>📊 多维度分析图表</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <h3>AI成熟度分布</h3>
                        <canvas id="maturityChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>创新水平分析</h3>
                        <canvas id="innovationChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>商业潜力分布</h3>
                        <canvas id="commercialChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>技术栈分布</h3>
                        <canvas id="techStackChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>AI框架使用情况</h3>
                        <canvas id="frameworkChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>社区健康状态</h3>
                        <canvas id="communityChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- 前沿技术项目 -->
            <div class="section">
                <h2>🔬 前沿技术项目</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>项目</th>
                                <th>综合评分</th>
                                <th>星标</th>
                                <th>前沿性评分</th>
                                <th>创新水平</th>
                                <th>最后提交</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # 添加前沿技术项目
    trending_projects = data.get('trending_projects', [])
    for project in trending_projects:
        score_class = "score-excellent" if project.get('enhanced_score', 0) >= 80 else \
                     "score-good" if project.get('enhanced_score', 0) >= 60 else \
                     "score-fair" if project.get('enhanced_score', 0) >= 40 else "score-poor"
        
        last_commit = project.get('last_commit_date', '')
        if last_commit:
            try:
                commit_date = datetime.fromisoformat(last_commit.replace('Z', '+00:00'))
                last_commit = commit_date.strftime('%Y-%m-%d')
            except:
                last_commit = 'Unknown'
        
        html_content += f"""
                            <tr>
                                <td><strong>{project.get('owner', '')}/{project.get('name', '')}</strong></td>
                                <td class="{score_class}">{project.get('enhanced_score', 0):.1f}</td>
                                <td>{project.get('stars', 0):,}</td>
                                <td><strong>{project.get('cutting_edge_score', 0)}</strong></td>
                                <td><span class="badge badge-{project.get('innovation_level', 'unknown')}">{project.get('innovation_level', 'Unknown')}</span></td>
                                <td>{last_commit}</td>
                            </tr>
        """
    
    # 准备图表数据
    maturity_data = data.get('ai_maturity_distribution', [])
    innovation_data = data.get('innovation_analysis', [])
    commercial_data = data.get('commercial_potential', [])
    tech_stack_data = data.get('technology_stack', [])
    framework_data = data.get('ai_frameworks', [])
    community_data = data.get('community_health', [])
    
    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 GitHub AI项目增强指标监控系统 | 基于Cloudflare D1数据库 | 数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
    </div>
    
    <script>
        // AI成熟度分布图
        const maturityCtx = document.getElementById('maturityChart').getContext('2d');
        new Chart(maturityCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([item.get('ai_maturity_level', 'Unknown') for item in maturity_data])},
                datasets: [{{
                    data: {json.dumps([item.get('count', 0) for item in maturity_data])},
                    backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#6c757d']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 创新水平分析图
        const innovationCtx = document.getElementById('innovationChart').getContext('2d');
        new Chart(innovationCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([item.get('innovation_level', 'Unknown') for item in innovation_data])},
                datasets: [{{
                    label: '项目数量',
                    data: {json.dumps([item.get('count', 0) for item in innovation_data])},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // 商业潜力分布图
        const commercialCtx = document.getElementById('commercialChart').getContext('2d');
        new Chart(commercialCtx, {{
            type: 'pie',
            data: {{
                labels: {json.dumps([item.get('commercial_potential', 'Unknown') for item in commercial_data])},
                datasets: [{{
                    data: {json.dumps([item.get('count', 0) for item in commercial_data])},
                    backgroundColor: ['#28a745', '#fd7e14', '#ffc107', '#6c757d']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 技术栈分布图
        const techStackCtx = document.getElementById('techStackChart').getContext('2d');
        new Chart(techStackCtx, {{
            type: 'horizontalBar',
            data: {{
                labels: {json.dumps([item.get('primary_language', 'Unknown') for item in tech_stack_data])},
                datasets: [{{
                    label: '项目数量',
                    data: {json.dumps([item.get('count', 0) for item in tech_stack_data])},
                    backgroundColor: '#764ba2'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // AI框架使用情况图
        const frameworkCtx = document.getElementById('frameworkChart').getContext('2d');
        new Chart(frameworkCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([item.get('ai_framework', 'Unknown') for item in framework_data])},
                datasets: [{{
                    data: {json.dumps([item.get('count', 0) for item in framework_data])},
                    backgroundColor: ['#e83e8c', '#fd7e14', '#20c997', '#6f42c1', '#dc3545']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 社区健康状态图
        const communityCtx = document.getElementById('communityChart').getContext('2d');
        new Chart(communityCtx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps([item.get('community_health', 'Unknown') for item in community_data])},
                datasets: [{{
                    label: '项目数量',
                    data: {json.dumps([item.get('count', 0) for item in community_data])},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.2)'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    return html_content

def main_generate_dashboard():
    """生成增强指标仪表板"""
    print("🎯 开始生成增强指标仪表板...")
    
    # 获取数据
    print("📊 正在获取数据库数据...")
    data = fetch_dashboard_data()
    
    if not data:
        print("❌ 无法获取数据")
        return
    
    # 生成HTML
    print("🎨 正在生成HTML仪表板...")
    html_content = generate_html_dashboard(data)
    
    # 保存文件
    output_file = "enhanced_metrics_dashboard.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 仪表板已生成: {output_file}")
    print(f"🌐 请在浏览器中打开 {os.path.abspath(output_file)} 查看")

if __name__ == "__main__":
    main_generate_dashboard()
