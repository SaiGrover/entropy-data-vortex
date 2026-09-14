# -*- coding: utf-8 -*-
"""Generate Phase 1 EDA Insight Report as PDF using fpdf2."""
from fpdf import FPDF
import os

def sanitize(text):
    replacements = {
        '—': '--', '–': '-', '‘': "'", '’': "'",
        '“': '"', '”': '"', '•': '*', '…': '...',
        '→': '->', '✓': 'Y', '×': 'x', '≥': '>=',
        '≤': '<=', 'ρ': 'rho', 'α': 'alpha', 'χ': 'chi',
        'σ': 'sigma', '∼': '~', '≈': '~',
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text

class EDAReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, 'Data Vortex | Team Entropy | EDA Insight Report', align='L')
            self.cell(0, 8, f'Page {self.page_no()}', align='R', new_x='LMARGIN', new_y='NEXT')
            self.line(10, 16, 200, 16)
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "AARUUSH'26 - Rebuilding the Social Engine - Team Entropy", align='C')

    def title_page(self):
        self.add_page()
        self.ln(50)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(44, 62, 80)
        self.cell(0, 15, 'Exploratory Data Analysis', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 15, 'Insight Report', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Round 1, Phase 1: Data Recovery', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(15)
        self.set_draw_color(52, 152, 219)
        self.set_line_width(1)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(15)
        self.set_font('Helvetica', '', 12)
        self.set_text_color(80, 80, 80)
        for line in [
            "Competition: Data Vortex | AARUUSH'26",
            'Theme: Rebuilding the Social Engine',
            'Team: Entropy',
            'Members: Saanvi Grover & Aditya Sharma',
            '',
            'Datasets: 12,000 posts | 1,500 users | 5 platforms',
            'Period: May 2024 -- April 2025 (364 days)',
            '20 analytical sections | 21 visualizations',
            '6 formal statistical significance tests',
        ]:
            self.cell(0, 8, sanitize(line), align='C', new_x='LMARGIN', new_y='NEXT')

    def toc_page(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(44, 62, 80)
        self.cell(0, 12, 'Table of Contents', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)
        sections = [
            ('1', 'Dataset Overview'),
            ('2', 'Platform Analysis: Does Platform Choice Matter?'),
            ('3', 'Temporal Analysis: When Should You Post?'),
            ('4', 'Engagement Distributions: Is There Viral Content?'),
            ('5', 'User Analysis: Do Followers Equal Influence?'),
            ('6', 'Geographic Analysis'),
            ('7', 'Language Analysis'),
            ('8', 'Content Analysis: Hashtags'),
            ('9', 'Content Analysis: Brands'),
            ('10', 'Sentiment Indicators'),
            ('11', 'Anomaly Detection'),
            ('12', 'Missing Data Analysis'),
            ('13', 'Key Insights Summary'),
            ('14', 'Statistical Significance Testing'),
            ('15', 'Brand x Platform Cross-Analysis'),
            ('16', 'Text Length Analysis'),
            ('17', 'Quantifying Uniformity: Coefficient of Variation'),
            ('18', 'Contradictory Sentiment Deep Dive'),
            ('19', 'Multi-Brand Posts & Engagement'),
            ('20', 'Analytical Narrative'),
            ('A', 'Conclusions & Recommendations'),
        ]
        self.set_font('Helvetica', '', 10)
        for num, title in sections:
            self.set_text_color(52, 152, 219)
            self.cell(12, 7, num, align='R')
            self.set_text_color(60, 60, 60)
            self.cell(5, 7, '')
            self.cell(0, 7, sanitize(title), new_x='LMARGIN', new_y='NEXT')

    def section_title(self, text):
        if self.get_y() > 230:
            self.add_page()
        self.ln(3)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, sanitize(text), new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(52, 152, 219)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, sanitize(text))
        self.ln(2)

    def add_image_safe(self, path, w=170):
        if os.path.exists(path):
            if self.get_y() > 180:
                self.add_page()
            self.image(path, x=20, w=w)
            self.ln(5)

    def insight_box(self, text):
        if self.get_y() > 240:
            self.add_page()
        self.set_fill_color(235, 245, 255)
        self.set_draw_color(52, 152, 219)
        self.set_line_width(0.3)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(41, 128, 185)
        self.cell(0, 6, 'KEY INSIGHT', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 9)
        self.set_text_color(44, 62, 80)
        self.multi_cell(0, 5, sanitize(text), fill=True)
        self.ln(4)

    def new_section_page(self):
        """Only add a new page if we're past the midpoint."""
        if self.get_y() > 140:
            self.add_page()


pdf = EDAReport()
pdf.set_auto_page_break(auto=True, margin=20)

# --- TITLE PAGE ---
pdf.title_page()

# --- TOC ---
pdf.toc_page()

# --- SECTION 1: Dataset Overview ---
pdf.add_page()
pdf.section_title('1. Dataset Overview')
pdf.body_text(
    "The Social Engine dataset consists of two tables recovered from Archive Node 07 "
    "on the competition's recovery terminal. After cleaning (Phase 1a), the final datasets are:"
)
pdf.body_text(
    'Posts Dataset: 12,000 rows x 8 columns (post_id, user_id, platform, text_content, '
    'timestamp, likes, shares, comments). Date range spans 364 days from May 2024 to April 2025.'
)
pdf.body_text(
    'Users Dataset: 1,500 rows x 5 columns (user_id, location, language, account_created, '
    'follower_count). Users created between Jan-Dec 2023 across 33 cities and 10 languages.'
)
pdf.body_text(
    'Missing data remains in three columns: platform (14.9%), text_content (14.3%), and '
    'likes (15.1%). These were left as NaN because no reliable imputation basis exists -- '
    'the corruption was confirmed to be Missing Completely at Random (MCAR) through '
    'statistical testing (Mann-Whitney U, p=0.64).'
)

# --- SECTION 2: Platform Analysis ---
pdf.section_title('2. Platform Analysis: Does Platform Choice Matter?')
pdf.body_text(
    'Purpose: In real social media, Instagram drives 2-3x more engagement than Twitter. '
    'Here we test whether platform choice matters in the Social Engine dataset.'
)
pdf.add_image_safe('images/Entropy_eda_platform_distribution.png')
pdf.body_text(
    'The left chart shows post counts by platform. Activity is nearly uniform: Facebook leads '
    'with 2,074 posts and Instagram trails at 1,989 -- a mere 4.3% spread. This uniformity is '
    'unusual for real social media and may reflect how the synthetic data was generated.'
)
pdf.add_image_safe('images/Entropy_eda_engagement_by_platform.png')
pdf.body_text(
    'Average engagement metrics (likes, shares, comments) are nearly identical across all '
    'five platforms. A Kruskal-Wallis test (Section 14) confirms this: H=4.27, p=0.37 -- '
    'platform choice does NOT significantly affect engagement.'
)
pdf.insight_box(
    'So What? Platform distribution is remarkably uniform (~2,000 posts each). Unlike real '
    'social media where platform dynamics vary dramatically, engagement here is platform-agnostic. '
    'This means Phase 2 SQL queries testing platform effects will find flat results -- not a '
    'failure, but a structural property of the data.'
)

# --- SECTION 3: Temporal Analysis ---
pdf.new_section_page()
pdf.section_title('3. Temporal Analysis: When Should You Post?')
pdf.body_text(
    'Purpose: Real platforms show 2-3x hourly variation and 20-40% day-of-week swings. '
    'We test whether timing matters in this dataset.'
)
pdf.add_image_safe('images/Entropy_eda_monthly_posts.png')
pdf.body_text(
    'Monthly post volume is stable around 914-1,038 posts/month. February 2025 is the lowest '
    '(914 posts, -9.2% MoM), likely reflecting the shorter month. March 2025 rebounds sharply '
    '(+10.8%). No seasonal trend is evident.'
)
pdf.add_image_safe('images/Entropy_eda_temporal_patterns.png')
pdf.body_text(
    'Left: Day-of-week posting shows Wednesday as the most active day (1,771 posts) and '
    'Saturday the least (1,675). The spread is narrow at 5.7%. '
    'Right: Hourly analysis reveals a nearly flat distribution across all 24 hours. '
    'Unlike real social media (which shows strong peaks during lunch and evening), this dataset '
    'has users posting at 3 AM as often as 7 PM.'
)
pdf.insight_box(
    'So What? Temporal patterns are unusually flat. Real social platforms show 2-3x variation by '
    'hour of day and 20-40% variation by day of week. This dataset shows <6% variation on both, '
    'suggesting timestamps were generated uniformly rather than reflecting real human behaviour.'
)

# --- SECTION 4: Engagement Distributions ---
pdf.new_section_page()
pdf.section_title('4. Engagement Distributions: Is There Viral Content?')
pdf.body_text(
    'Purpose: Real social media follows power-law distributions (few viral posts, many '
    'low-engagement). We test whether this dataset has outliers.'
)
pdf.add_image_safe('images/Entropy_eda_engagement_distributions.png')
pdf.body_text(
    'All three metrics follow near-uniform distributions, not the heavy-tailed (power-law) '
    'distributions typical of real social media. Likes range from 0 to 5,000 with mean ~2,492 '
    'and median ~2,498 (nearly identical, confirming symmetry). The mean-median proximity means '
    'there are no viral outliers -- every post gets roughly similar engagement.'
)
pdf.add_image_safe('images/Entropy_eda_engagement_correlation.png')
pdf.body_text(
    'The correlation heatmap reveals weak relationships between all three metrics. '
    'Likes-shares correlation is only 0.003, likes-comments is -0.003, and shares-comments '
    'is -0.010. In real social media, these metrics are typically positively correlated.'
)
pdf.insight_box(
    'So What? Engagement metrics are uniformly distributed and statistically independent. This is '
    'the opposite of real social media where engagement follows power-law distributions and '
    'metrics are positively correlated.'
)

# --- SECTION 5: User Analysis ---
pdf.new_section_page()
pdf.section_title('5. User Analysis: Do Followers Equal Influence?')
pdf.body_text(
    'Purpose: On real platforms, follower count is the #1 predictor of reach. '
    'We test whether that holds in this dataset.'
)
pdf.add_image_safe('images/Entropy_eda_user_activity.png')
pdf.body_text(
    'Left: The posts-per-user distribution is right-skewed. Mean is 8.0 posts/user, ranging '
    'from 1 to 22. Right: Follower count vs. post count shows no visible relationship -- the '
    'scatter plot is a uniform cloud. A Spearman correlation test confirms: rho=0.025, p=0.34 '
    '(not significant). Follower count does not predict activity or engagement.'
)
pdf.insight_box(
    'So What? Follower count has zero predictive power -- contradicting real social media dynamics '
    'where follower count is the strongest predictor of reach.'
)

# --- SECTION 6: Geographic Analysis ---
pdf.section_title('6. Geographic Analysis')
pdf.body_text(
    'Purpose: Map the geographic distribution of users and identify whether location '
    'influences engagement levels.'
)
pdf.add_image_safe('images/Entropy_eda_geographic.png')
pdf.body_text(
    'Users span 33 cities across 6 continents. Shanghai leads with 56 users (3.7%). '
    'Average likes by location show modest variation (2,300-2,700 range). No single city '
    'or region dominates engagement.'
)

# --- SECTION 7: Language Analysis ---
pdf.section_title('7. Language Analysis')
pdf.body_text(
    'Purpose: Examine how the 10 language communities differ in size and engagement patterns.'
)
pdf.add_image_safe('images/Entropy_eda_language.png')
pdf.body_text(
    'All 10 languages have between 119-168 users. Average engagement by language is remarkably '
    'flat -- the engagement generation process was language-independent.'
)

# --- SECTION 8: Hashtag Analysis ---
pdf.section_title('8. Content Analysis: Hashtags')
pdf.body_text(
    'Purpose: Extract and rank hashtags from post text to identify dominant content themes.'
)
pdf.add_image_safe('images/Entropy_eda_top_hashtags.png')
pdf.body_text(
    'The top 20 hashtags reveal consumer-focused themes: #Fashion, #Sale, #Tech, #Health. '
    'These are generic commercial hashtags consistent with brand-centric post templates.'
)

# --- SECTION 9: Brand Analysis ---
pdf.new_section_page()
pdf.section_title('9. Content Analysis: Brands')
pdf.body_text(
    'Purpose: Identify which of the 10 embedded brands are mentioned most frequently and '
    'whether brand mentions correlate with higher engagement.'
)
pdf.add_image_safe('images/Entropy_eda_brand_analysis.png')
pdf.body_text(
    'All 10 brands appear in roughly 1,000-1,100 posts each. Average likes per brand post are '
    'nearly identical (2,450-2,550 range). No brand drives significantly more engagement. '
    'Engagement is independent of both platform and brand.'
)

# --- SECTION 10: Sentiment ---
pdf.section_title('10. Sentiment Indicators')
pdf.body_text(
    'Purpose: Classify post sentiment using keyword matching to understand the emotional '
    'tone distribution and whether sentiment predicts engagement.'
)
pdf.add_image_safe('images/Entropy_eda_sentiment.png')
pdf.body_text(
    'A notable finding is the "Contradictory" category -- posts containing both positive and '
    'negative phrases (e.g., "Bummed out... Absolutely loving it") -- which reflects template-'
    'based text generation. Negative posts get slightly higher engagement than positive -- '
    'the "outrage engagement" pattern seen in real social media research.'
)
pdf.insight_box(
    'Contradictory sentiment posts are a signature of template-based text generation. This is '
    'a data quality observation worth flagging in competition analysis.'
)

# --- SECTION 11: Anomaly Detection ---
pdf.section_title('11. Anomaly Detection')
pdf.body_text(
    'Purpose: Use IQR-based statistical methods to identify outlier posts with unusually '
    'high or low engagement.'
)
pdf.add_image_safe('images/Entropy_eda_anomalies.png')
pdf.body_text(
    'The IQR method finds zero outlier posts for likes -- every post falls within expected '
    'statistical bounds. This is highly unusual: real social media datasets always have outliers '
    '(viral posts). The likes-vs-shares scatter shows a uniform cloud with no clustering.'
)

# --- SECTION 12: Missing Data ---
pdf.section_title('12. Missing Data Analysis')
pdf.body_text(
    'Purpose: Determine whether missing values are random or systematic.'
)
pdf.add_image_safe('images/Entropy_eda_missing_patterns.png')
pdf.body_text(
    'The missingness correlation heatmap shows weak correlations between missing indicators, '
    'confirming Missing Completely at Random (MCAR). A Mann-Whitney U test confirms posts with '
    'missing platform data have statistically similar engagement (p=0.64), validating our '
    'cleaning decision to retain missing values as NaN.'
)

# --- SECTION 13: Key Insights ---
pdf.new_section_page()
pdf.section_title('13. Key Insights Summary')
pdf.body_text('The 20 analytical sections reveal these core findings:')
pdf.body_text(
    '1. STRUCTURAL UNIFORMITY: Engagement, platform distribution, brand mentions, language '
    'communities, and temporal patterns are all remarkably flat -- the defining characteristic '
    'of this dataset.'
)
pdf.body_text(
    '2. NO VIRAL CONTENT: Zero posts exceed the IQR outlier threshold. Every post receives '
    '"average" engagement. Real social data always has power-law tails.'
)
pdf.body_text(
    '3. INDEPENDENT METRICS: Likes, shares, and comments are uncorrelated (r < 0.01). '
    'Each was generated independently.'
)
pdf.body_text(
    '4. FOLLOWER COUNT IS DECORATIVE: No correlation with engagement (Spearman rho=0.025, '
    'p=0.34). In real platforms, this is the strongest predictor of reach.'
)
pdf.body_text(
    '5. CORRUPTION WAS RANDOM: Missing data is MCAR, engagement is unaffected by completeness.'
)
pdf.body_text(
    '6. TEMPLATE-GENERATED TEXT: Contradictory sentiment phrases, uniform brand distribution, '
    'and generic hashtags point to template-based content generation.'
)
pdf.body_text(
    '7. ONE GENUINE SIGNAL: Multi-platform users show ~15% higher engagement -- the only '
    'statistically significant finding across all 6 hypothesis tests.'
)
pdf.body_text(
    '8. CV CONFIRMS UNIFORMITY: Coefficient of variation < 10% on most dimensions formally '
    'quantifies the uniformity with a standard statistical measure.'
)

# --- SECTION 14: Statistical Tests ---
pdf.section_title('14. Statistical Significance Testing')
pdf.body_text(
    'Purpose: Formally test whether observed patterns are statistically significant, '
    'using non-parametric tests suited to non-normal distributions.'
)
pdf.body_text(
    'Test 1 -- Kruskal-Wallis (platforms vs likes): H=4.27, p=0.37. NOT significant.'
)
pdf.body_text(
    'Test 2 -- Kruskal-Wallis (day-of-week vs engagement): H=3.72, p=0.71. NOT significant.'
)
pdf.body_text(
    'Test 3 -- Chi-square (sentiment x platform): chi2=23.94, p=0.24. NOT significant.'
)
pdf.body_text(
    'Test 4 -- Spearman (follower count vs likes): rho=0.025, p=0.34. NOT significant.'
)
pdf.body_text(
    'Test 5 -- Mann-Whitney U (missing platform vs engagement): U=9,175,298, p=0.64. '
    'NOT significant. Confirms MCAR.'
)
pdf.body_text(
    'Test 6 -- Kruskal-Wallis (multi-platform users vs engagement): Multi-platform users '
    'show ~15% higher engagement -- the ONE genuine signal in the dataset.'
)
pdf.insight_box(
    'Five of six tests return p > 0.05. The sixth test (multi-platform user behaviour) '
    'is the one genuine signal worth investigating in subsequent rounds.'
)

# --- SECTION 15: Brand x Platform ---
pdf.new_section_page()
pdf.section_title('15. Brand x Platform Cross-Analysis')
pdf.body_text(
    'Purpose: Test whether certain brands perform better on specific platforms.'
)
pdf.add_image_safe('images/Entropy_eda_brand_platform_heatmap.png')
pdf.body_text(
    'Average likes by brand x platform shows values in the 2,300-2,700 range with no obvious '
    'hot spots. Post volume by brand x platform is remarkably even (~200 posts per cell). '
    'No brand-platform affinity exists.'
)
pdf.insight_box(
    'Unlike real social media where Nike dominates Instagram and tech brands lead on Reddit, '
    'this dataset shows no brand-platform affinity -- useful context for Phase 2 SQL analysis.'
)

# --- SECTION 16: Text Length ---
pdf.section_title('16. Text Length Analysis')
pdf.body_text(
    'Purpose: Examine whether post length varies by platform and predicts engagement.'
)
pdf.add_image_safe('images/Entropy_eda_text_length_analysis.png')
pdf.body_text(
    'Character length peaks around 80-120 characters. Word count centers around 15-25 words. '
    'All platforms have similar median word counts (~18-20 words). Word count vs likes shows '
    'near-zero correlation. Post length does not predict engagement.'
)

# --- SECTION 17: Coefficient of Variation ---
pdf.new_section_page()
pdf.section_title('17. Quantifying Uniformity: Coefficient of Variation')
pdf.body_text(
    'Purpose: Formally quantify uniformity using the Coefficient of Variation '
    '(CV = std/mean x 100). A CV below 10% indicates very low variation.'
)
pdf.add_image_safe('images/Entropy_eda_coefficient_of_variation.png')
pdf.body_text(
    'The CV analysis confirms what earlier sections observed qualitatively: most dimensions '
    'have CV < 10%. Platform volume, day-of-week volume, brand mentions, and language '
    'distribution are all structurally flat. This level of uniformity is never seen in real '
    'social media data, where power-law dynamics create typical CV > 50%.'
)
pdf.insight_box(
    "The coefficient of variation formally quantifies the dataset's structural uniformity. "
    'With most metrics showing CV < 10%, we can state with confidence that the data was generated '
    'from uniform distributions -- not sampled from real user behaviour.'
)

# --- SECTION 18: Contradictory Sentiment Deep Dive ---
pdf.new_section_page()
pdf.section_title('18. Contradictory Sentiment Deep Dive')
pdf.body_text(
    'Purpose: Investigate posts containing BOTH positive and negative sentiment phrases. '
    'How many exist? What phrase combinations appear? Can we reverse-engineer the templates?'
)
pdf.add_image_safe('images/Entropy_eda_contradictory_sentiment_deep_dive.png')
pdf.body_text(
    'Left: Top contradictory phrase pairs reveal combinations like "disappointed + loving it" '
    'appearing in the same post -- artifacts of a text generator inserting sentiment phrases '
    'independently into template structures. Right: Template structure analysis shows posts '
    'follow identifiable patterns (unboxing, reviews, ad reactions, comparisons, complaints).'
)
pdf.insight_box(
    'The deep dive confirms template-based text generation. Sentiment phrases are "slotted in" '
    'without regard for consistency -- explaining why sentiment does not predict engagement.'
)

# --- SECTION 19: Multi-Brand Posts ---
pdf.new_section_page()
pdf.section_title('19. Multi-Brand Posts & Engagement')
pdf.body_text(
    'Purpose: Test whether posts mentioning multiple brands receive different engagement '
    'than single-brand posts.'
)
pdf.add_image_safe('images/Entropy_eda_multi_brand_engagement.png')
pdf.body_text(
    'Average likes by brand count tests whether content density (more brands = more information) '
    'affects engagement. A Mann-Whitney U test compares single-brand vs multi-brand posts. '
    'This adds a dimension most teams will not explore: treating brand mentions as a count '
    'variable rather than a categorical variable.'
)

# --- SECTION 20: Analytical Narrative ---
pdf.new_section_page()
pdf.section_title('20. Analytical Narrative: The Story This Data Tells')
pdf.body_text('THE CENTRAL FINDING: STRUCTURAL UNIFORMITY')
pdf.body_text(
    'This EDA reveals that the Social Engine dataset is structurally uniform to a degree never '
    'seen in real social media. The CV analysis (Section 17) quantifies this: platform volume, '
    'day-of-week patterns, brand mentions, and language distribution all have CV < 10%.'
)
pdf.body_text('WHY THIS MATTERS FOR THE COMPETITION')
pdf.body_text(
    "Understanding uniformity is not a limitation -- it IS the insight. "
    'For Phase 2: Queries testing for viral content and bot detection will return empty results '
    "-- proving the analyst understands the data's structure. "
    'For Phase 3: Multi-platform users are the focus; traditional signals are dead ends. '
    'For Phase 4: A dashboard that honestly surfaces "no effect found" is more valuable than '
    'one that cherry-picks weak patterns.'
)
pdf.body_text('THE ONE REAL SIGNAL')
pdf.body_text(
    'Of all dimensions tested, only multi-platform user behaviour shows a statistically '
    'significant effect (~15% higher engagement). This is the thread worth pulling.'
)
pdf.body_text('SYNTHETIC VS REAL COMPARISON')
pdf.body_text(
    'Platform engagement: Real expects 2-3x variation, dataset shows <5% -> Synthetic. '
    'Hourly posting: Real shows strong peaks, dataset flat -> Synthetic. '
    'Follower correlation: Real r>0.3, dataset r=0.025 -> Synthetic. '
    'Multi-platform advantage: 15% higher (significant) -> Possibly real. '
    'Template text: Confirmed via contradictory sentiment -> Data generation artifact.'
)
pdf.insight_box(
    'The analytical narrative connects all 20 sections: structural uniformity is the defining '
    'characteristic, with one genuine signal (multi-platform users) and one original finding '
    '(template-based text generation with contradictory sentiment).'
)

# --- CONCLUSIONS ---
pdf.new_section_page()
pdf.section_title('Conclusions & Recommendations')
pdf.body_text(
    'This EDA establishes the fundamental character of the Social Engine dataset through '
    '20 analytical sections, 21 visualizations, and 6 statistical tests. The dataset is '
    'structurally uniform (CV < 10% on most dimensions), with engagement generated independently '
    'of user attributes, platform, timing, or content. Two genuine signals emerge: '
    'multi-platform users show significantly higher engagement (~15%), and template-based text '
    'generation creates detectable contradictory sentiment patterns.'
)
pdf.body_text('Recommendations for Phase 2 (SQL Analysis):')
pdf.body_text(
    '1. Trend Detection: Focus on monthly volume and growth rates. Day-of-week and platform '
    'trends will be flat but should still be demonstrated with proper window functions.'
)
pdf.body_text(
    '2. Anomaly Discovery: Q4 (viral posts) and Q5 (bot detection) will return empty results, '
    'but the queries demonstrate advanced statistical SQL and the empty results are a '
    'legitimate finding.'
)
pdf.body_text(
    '3. Behavioural Grouping: Multi-platform users are the one dimension where a real signal '
    'exists (15% higher engagement for 5-platform users).'
)
pdf.body_text(
    '4. Correlation Analysis: Follower count vs engagement will be flat. Brand sentiment '
    'analysis is the most promising direction.'
)

# --- APPENDIX ---
pdf.new_section_page()
pdf.section_title('Appendix: Corruption Catalog')
pdf.body_text(
    'The following corruption patterns were identified and fixed during Phase 1a cleaning.'
)
pdf.add_image_safe('images/Entropy_corruption_catalog.png')
pdf.add_image_safe('images/Entropy_data_quality_scorecard.png')
pdf.body_text(
    'The data quality scorecard shows: 360 duplicate rows removed, 974 HTML artifacts cleaned, '
    '306 mojibake instances fixed, 509 negative likes corrected, 24 NULL strings replaced, '
    'and all 12,000 timestamps standardized.'
)

# --- OUTPUT ---
output_path = 'Entropy_Phase1_EDA_Report.pdf'
pdf.output(output_path)
print(f'Generated: {output_path} ({os.path.getsize(output_path) / 1024:.0f} KB)')
