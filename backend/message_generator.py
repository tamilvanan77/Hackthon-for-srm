"""
Parent Communication Generator
Generates sensitive, stigma-free messages in English and Tamil.
"""


def generate_parent_message(student_name, language="english", concerns=None):
    """
    Generate a sensitive parent communication message.

    Rules:
    - Never use: 'dropout', 'failing', 'at risk', 'poor performance'
    - Use encouraging, supportive language
    - Focus on partnership between school and parent

    Args:
        student_name: Name of the student
        language: 'english' or 'tamil'
        concerns: list of concern areas (attendance, academics, engagement)

    Returns:
        str: Generated message
    """
    if concerns is None:
        concerns = ["attendance"]

    if language == "tamil":
        return _generate_tamil(student_name, concerns)
    else:
        return _generate_english(student_name, concerns)


def _generate_english(name, concerns):
    """Generate English parent message."""

    greeting = f"Dear Parent / Guardian of {name},"
    closing = (
        "We believe that with your support, your child can achieve great things. "
        "Please feel free to contact us to discuss how we can work together.\n\n"
        "With warm regards,\n"
        "School Administration"
    )

    concern_paragraphs = []

    if "attendance" in concerns:
        concern_paragraphs.append(
            f"We have noticed that {name}'s school attendance has been "
            f"less regular recently. Regular attendance helps students "
            f"stay connected with their classmates, participate in activities, "
            f"and make the most of each learning opportunity."
        )

    if "academics" in concerns:
        concern_paragraphs.append(
            f"We would like to share that {name} could benefit from "
            f"additional support in some subjects. Our teachers are ready "
            f"to provide extra guidance, and with practice at home, "
            f"we are confident {name} will show wonderful improvement."
        )

    if "engagement" in concerns:
        concern_paragraphs.append(
            f"We have observed that {name} has been quieter in class "
            f"activities lately. Participating in school events and "
            f"interacting with classmates builds confidence and makes "
            f"school a more enjoyable experience."
        )

    if "distance" in concerns:
        concern_paragraphs.append(
            f"We understand that travelling to school can sometimes be "
            f"challenging. We would like to discuss available support options, "
            f"including transportation assistance programs, that could help "
            f"make the daily journey easier for {name}."
        )

    if "economic" in concerns:
        concern_paragraphs.append(
            f"We want to ensure that {name} has every opportunity to "
            f"continue learning without any barriers. There are several "
            f"government support programs available that your family may "
            f"be eligible for. We would be happy to help with the application "
            f"process."
        )

    if not concern_paragraphs:
        concern_paragraphs.append(
            f"We are reaching out to share an update about {name}'s "
            f"school experience. Your involvement makes a tremendous "
            f"difference in your child's learning journey."
        )

    body = "\n\n".join(concern_paragraphs)

    return f"""{greeting}

Greetings from the school! We hope this message finds you well.

{body}

{closing}"""


def _generate_tamil(name, concerns):
    """Generate Tamil parent message."""

    greeting = f"மதிப்பிற்குரிய {name} அவர்களின் பெற்றோர் / பாதுகாவலர் அவர்களுக்கு,"
    closing = (
        "உங்கள் ஆதரவுடன், உங்கள் குழந்தை சிறந்த சாதனைகளை எட்ட முடியும் என்று "
        "நாங்கள் நம்புகிறோம். நாம் எவ்வாறு ஒன்றாகச் செயல்படலாம் என்பதை "
        "விவாதிக்க எங்களைத் தொடர்பு கொள்ளவும்.\n\n"
        "அன்புடன்,\n"
        "பள்ளி நிர்வாகம்"
    )

    concern_paragraphs = []

    if "attendance" in concerns:
        concern_paragraphs.append(
            f"{name} அவர்களின் பள்ளி வருகை சமீபத்தில் குறைந்துள்ளது என்பதை "
            f"நாங்கள் கவனித்துள்ளோம். தொடர்ச்சியான வருகை மாணவர்கள் தங்கள் "
            f"சக மாணவர்களுடன் இணைந்திருக்கவும், செயல்பாடுகளில் பங்கேற்கவும், "
            f"ஒவ்வொரு கற்றல் வாய்ப்பையும் பயன்படுத்திக்கொள்ளவும் உதவுகிறது."
        )

    if "academics" in concerns:
        concern_paragraphs.append(
            f"சில பாடங்களில் {name} அவர்களுக்கு கூடுதல் உதவி பயனளிக்கும் "
            f"என்பதைப் பகிர்ந்து கொள்ள விரும்புகிறோம். எங்கள் ஆசிரியர்கள் "
            f"கூடுதல் வழிகாட்டுதல் வழங்கத் தயாராக உள்ளனர், வீட்டில் "
            f"பயிற்சியுடன் {name} அருமையான முன்னேற்றம் காட்டுவார் என்று "
            f"நாங்கள் நம்புகிறோம்."
        )

    if "engagement" in concerns:
        concern_paragraphs.append(
            f"வகுப்பு நடவடிக்கைகளில் {name} சமீபத்தில் அமைதியாக "
            f"இருப்பதைக் கவனித்துள்ளோம். பள்ளி நிகழ்வுகளில் பங்கேற்பது "
            f"தன்னம்பிக்கையை வளர்ப்பதுடன் பள்ளியை மேலும் "
            f"மகிழ்ச்சிகரமான அனுபவமாக மாற்றுகிறது."
        )

    if "distance" in concerns:
        concern_paragraphs.append(
            f"பள்ளிக்கு பயணம் செய்வது சில நேரங்களில் சவாலாக இருக்கும் "
            f"என்பதை நாங்கள் புரிந்துகொள்கிறோம். {name} அவர்களின் "
            f"தினசரி பயணத்தை எளிதாக்க உதவும் போக்குவரத்து உதவித் "
            f"திட்டங்கள் பற்றி விவாதிக்க விரும்புகிறோம்."
        )

    if "economic" in concerns:
        concern_paragraphs.append(
            f"எந்தத் தடையும் இல்லாமல் {name} தொடர்ந்து கற்றுக் "
            f"கொள்வதை உறுதிசெய்ய விரும்புகிறோம். உங்கள் குடும்பம் "
            f"தகுதி பெறக்கூடிய பல அரசாங்க ஆதரவுத் திட்டங்கள் உள்ளன. "
            f"விண்ணப்ப செயல்முறையில் நாங்கள் உதவ மகிழ்ச்சியடைவோம்."
        )

    if not concern_paragraphs:
        concern_paragraphs.append(
            f"{name} அவர்களின் பள்ளி அனுபவம் பற்றிய தகவலைப் "
            f"பகிர்ந்து கொள்ள விரும்புகிறோம். உங்கள் ஈடுபாடு "
            f"உங்கள் குழந்தையின் கற்றல் பயணத்தில் மிகப்பெரிய "
            f"மாற்றத்தை ஏற்படுத்துகிறது."
        )

    body = "\n\n".join(concern_paragraphs)

    return f"""{greeting}

பள்ளியிலிருந்து வணக்கம்! இந்தச் செய்தி உங்களை நலமுடன் காணும் என்று நம்புகிறோம்.

{body}

{closing}"""


def generate_whatsapp_message(student_name, language="english", concerns=None):
    """Generate a shorter WhatsApp-friendly message."""
    if concerns is None:
        concerns = ["attendance"]

    if language == "tamil":
        return _whatsapp_tamil(student_name, concerns)
    else:
        return _whatsapp_english(student_name, concerns)


def _whatsapp_english(name, concerns):
    """Short English WhatsApp message."""
    concern_text = ""
    if "attendance" in concerns:
        concern_text = f"We noticed {name}'s attendance has been less regular recently. "
    elif "academics" in concerns:
        concern_text = f"We believe {name} would benefit from some extra practice in key subjects. "
    elif "engagement" in concerns:
        concern_text = f"We'd love to see {name} participate more in class activities. "
    else:
        concern_text = f"We'd like to share an update about {name}'s school experience. "

    return (
        f"🏫 Hello! This is {name}'s school.\n\n"
        f"{concern_text}"
        f"Your support makes a big difference in your child's learning journey.\n\n"
        f"Please visit the school or call us for a friendly conversation. "
        f"We're here to help! 🙏"
    )


def _whatsapp_tamil(name, concerns):
    """Short Tamil WhatsApp message."""
    concern_text = ""
    if "attendance" in concerns:
        concern_text = f"{name} அவர்களின் பள்ளி வருகை சமீபத்தில் குறைந்துள்ளது. "
    elif "academics" in concerns:
        concern_text = f"{name} சில முக்கிய பாடங்களில் கூடுதல் பயிற்சியால் பயனடைவார். "
    elif "engagement" in concerns:
        concern_text = f"{name} வகுப்பு நடவடிக்கைகளில் மேலும் பங்கேற்க விரும்புகிறோம். "
    else:
        concern_text = f"{name} அவர்களின் பள்ளி அனுபவம் பற்றிய தகவலை பகிர விரும்புகிறோம். "

    return (
        f"🏫 வணக்கம்! இது {name} அவர்களின் பள்ளி.\n\n"
        f"{concern_text}"
        f"உங்கள் ஆதரவு உங்கள் குழந்தையின் கற்றலில் பெரிய மாற்றத்தை ஏற்படுத்துகிறது.\n\n"
        f"பள்ளிக்கு வரவும் அல்லது எங்களை அழைக்கவும். நாங்கள் உதவ தயாராக உள்ளோம்! 🙏"
    )
