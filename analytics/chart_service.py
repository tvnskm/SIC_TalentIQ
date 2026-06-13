import io
import base64
import matplotlib
matplotlib.use('Agg')   # Non-interactive backend — required for Django
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set consistent visual theme
sns.set_theme(style='whitegrid', palette='muted')

def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string for HTML embedding."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded


class ChartService:
    
    def top_skills_chart(self, skills_data: list) -> str:
        """
        Seaborn horizontal bar chart — Top Skills by frequency.
        Input: [{'skill': 'Python', 'count': 45}, ...]
        """
        if not skills_data:
            return ""
        labels = [d['skill'] for d in skills_data]
        values = [d['count'] for d in skills_data]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=values, y=labels, ax=ax, hue=labels, palette='Blues_d', orient='h', legend=False)
        ax.set_title('Top Skills Across All Candidates', fontsize=14, fontweight='bold')
        ax.set_xlabel('Number of Candidates')
        ax.set_ylabel('Skill')
        return _fig_to_base64(fig)
    
    def experience_distribution_chart(self, stats: dict) -> str:
        """
        Matplotlib bar chart — Experience distribution by bucket.
        Input: stats['distribution'] = {'0-2 yrs': 5, ...}
        """
        if not stats or 'distribution' not in stats:
            return ""
        dist = stats['distribution']
        labels = list(dist.keys())
        values = list(dist.values())
        
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(labels, values, color='steelblue', edgecolor='white')
        ax.bar_label(bars, padding=3)
        ax.set_title('Experience Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Experience Range')
        ax.set_ylabel('Number of Candidates')
        plt.xticks(rotation=20)
        return _fig_to_base64(fig)
    
    def education_distribution_chart(self, dist: dict) -> str:
        """
        Matplotlib pie chart — Education level distribution.
        """
        if not dist:
            return ""
        labels = list(dist.keys())
        sizes  = list(dist.values())
        colors = sns.color_palette('pastel')[0:len(labels)]
        
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.set_title('Education Distribution', fontsize=14, fontweight='bold')
        return _fig_to_base64(fig)
    
    def match_score_histogram(self, dist: dict) -> str:
        """
        Seaborn histogram — Match percentage distribution.
        """
        if not dist:
            return ""
        # Expand bucket data back to approximate scores for histogram
        scores = []
        for bucket, count in dist.items():
            low = int(bucket.split('-')[0].replace('%','').strip())
            scores.extend([low + 10] * count)   # midpoint approximation
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(scores, bins=10, kde=True, ax=ax, color='teal')
        ax.set_title('Match Score Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Match Percentage')
        ax.set_ylabel('Frequency')
        return _fig_to_base64(fig)
    
    def certification_distribution_chart(self, dist: dict) -> str:
        """
        Seaborn count bar chart — Certifications per candidate.
        """
        if not dist:
            return ""
        labels = list(dist.keys())
        values = list(dist.values())
        
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=labels, y=values, ax=ax, hue=labels, palette='Set2', legend=False)
        ax.set_title('Certification Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Certifications per Candidate')
        ax.set_ylabel('Number of Candidates')
        return _fig_to_base64(fig)

    def generic_bar_chart(self, title: str, data: dict, xlabel: str, ylabel: str) -> str:
        if not data:
            return ""
        labels = list(data.keys())
        values = list(data.values())
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=values, y=labels, ax=ax, hue=labels, palette='Blues_d', orient='h', legend=False)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        return _fig_to_base64(fig)
        
    def generic_pie_chart(self, title: str, data: dict) -> str:
        if not data:
            return ""
        labels = list(data.keys())
        sizes  = list(data.values())
        colors = sns.color_palette('pastel')[0:len(labels)]
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.set_title(title, fontsize=14, fontweight='bold')
        return _fig_to_base64(fig)
