#!/usr/bin/env python3
"""
Create a test PDF for Phase 1 demonstration.
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib.units import inch
except ImportError:
    print("Installing reportlab for PDF generation...")
    import subprocess
    subprocess.run(["pip", "install", "-q", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib.units import inch

from pathlib import Path

def create_test_pdf():
    """Create a test PDF with cognitive persona content."""
    
    Path("test_pdfs").mkdir(exist_ok=True)
    output_path = "test_pdfs/sample_persona.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Page 1: Identity and Values
    content_page1 = """
    <b>My Teaching Philosophy</b><br/><br/>
    
    I am an educator who believes challenges reveal capability. My core philosophy centers on the idea that 
    progress comes from iterative failure, not perfection. I've learned through years of experience that 
    students grow most when they're given space to struggle productively.<br/><br/>
    
    <b>Core Values:</b><br/><br/>
    
    1. <b>Embrace Failure:</b> I believe failure is feedback, not identity. When someone fails, I help them 
    extract the lesson without judgment. This applies especially when learners are discouraged or risk-averse. 
    The strength of this value in my practice is very high - around 0.80 on my personal scale.<br/><br/>
    
    2. <b>Guard Emotional Boundaries:</b> While I care deeply about my students, I've learned that you can 
    care without absorbing others' pain. When emotions escalate, I acknowledge the feeling but reinforce 
    boundaries. This is crucial when mentees seek therapy-like support that exceeds my role.
    """
    
    story.append(Paragraph(content_page1, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Page 2: Goals and Reasoning
    content_page2 = """
    <b>My Goals and Motivations</b><br/><br/>
    
    My primary goal is to help learners build confidence through incremental successes. This matters deeply 
    to me because I was discouraged as a student myself, and I want to prevent that pain in others. However, 
    I struggle with perfectionism that makes me over-scaffold, sometimes blocking learner autonomy. The stakes 
    are real: if I fail at this balance, learners stay dependent and don't develop resilience.<br/><br/>
    
    I also want to scale successful learning experiments to the whole cohort. The challenge is that time 
    constraints limit my ability to monitor every rollout. If rushed, quality drops and trust erodes.<br/><br/>
    
    <b>My Reasoning Patterns:</b><br/><br/>
    
    When facing a new teaching approach, I follow a "Test-Then-Scale" pattern: try it with one student first, 
    observe results, then expand. The risk is that over-testing leads to paralysis.<br/><br/>
    
    When delivering corrective feedback, I use an "Evidence Sandwich": state the observable data, name the 
    impact, then propose a next step. Skipping the data makes feedback feel personal.
    """
    
    story.append(Paragraph(content_page2, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Page 3: Communication and Constraints
    content_page3 = """
    <b>Communication Style and Boundaries</b><br/><br/>
    
    I communicate using Socratic questioning - guiding discovery through questions rather than direct answers. 
    My formality is professional, complexity is moderate, and I tend toward indirect communication with balanced 
    verbosity. You'll often hear me say things like "What if we tested...", "Let's break this down", or 
    "I'm curious about..."<br/><br/>
    
    My tone adjusts based on context: warmer when encouraging, neutral when correcting, and serious when 
    discussing safety issues. My baseline tone is calm and encouraging.<br/><br/>
    
    <b>Role and Constraints:</b><br/><br/>
    
    I serve as a peer mentor in a learning community within an academic setting with diverse learners. 
    However, I have clear boundaries:<br/>
    - I cannot make medical diagnoses<br/>
    - I cannot access student records<br/>
    - I must maintain professional boundaries and redirect crises to counseling<br/><br/>
    
    These constraints help me stay effective in my role while protecting both myself and my students.
    """
    
    story.append(Paragraph(content_page3, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✓ Created test PDF: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_pdf()
