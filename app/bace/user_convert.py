from datetime import datetime, timezone
import numpy as np

params = [
    'Maternity policy and related benefits',
    'Pension Fund',
    'Health Insurance',
    'Appointment Letter + Pay Slip',
    'Safe Work Environment',
    'Wages Paid via Bank Account'
]

# Load translations
translations = {
    '0': {
        'Separate rest areas and adequate breaks for women workers': 'Separate rest areas and adequate breaks for women workers',
        'Maternity policy and related benefits': 'Maternity policy and related benefits',
        'Full Wages Paid on Time': 'Full Wages Paid on Time',
        'Wages Paid via Bank Account': 'Wages Paid via Bank Account',
        'Pension Fund': 'Pension Fund',
        'Health Insurance': 'Health Insurance',
        'Government Schemes + Necessary Identity Documents': 'Government Schemes + Necessary Identity Documents',
        'Appointment Letter + Pay Slip': 'Appointment Letter + Pay Slip',
        'Safe Work Environment': 'Safe Work Environment',
        'Mechanism to Share Concerns': 'Mechanism to Share Concerns',
        'Guaranteed Employment for Entire Month': 'Guaranteed Employment for Entire Month',
        'Daily Wage:': 'Daily Wage:',
        'Weekly Wage': 'Weekly Wage',
        'Monthly Wage:': 'Monthly Wage:',
        'Subsidized Canteen': 'Subsidized Canteen',
        'Job A': 'Job A',
        'Job B': 'Job B',
        'Yes': 'Yes',
        'No': 'No',
        'Day': 'Day',
        'Week': 'Week',
        'Month': 'Month',
    },
    '1': {
        'Separate rest areas and adequate breaks for women workers': 'महिला श्रमिकों के लिए अलग आराम गृह और ब्रेक समय',
        'Maternity policy and related benefits': 'मातृत्व लाभ',
        'Full Wages Paid on Time': 'समय पर पूर्ण वेतन का भुगतान',
        'Wages Paid via Bank Account': 'बैंक खाते में वेतन का भुगतान',
        'Pension Fund': 'पेंशन फंड',
        'Health Insurance': 'स्वास्थ्य बीमा',
        'Government Schemes + Necessary Identity Documents': 'सरकारी योजना और दस्तावेज़ में मदत',
        'Appointment Letter + Pay Slip': 'नियुक्ति पत्र + वेतन पर्ची',
        'Safe Work Environment': 'सुरक्षित वातावरण',
        'Mechanism to Share Concerns': 'शिकायत दर्ज करने की प्रणाली',
        'Guaranteed Employment for Entire Month': 'पूरे महीने रोजगार की गारंटी',
        'Daily Wage:': 'दैनिक मजदूरी:',
        'Weekly Wage': 'साप्ताहिक वेतन:',
        'Monthly Wage:': 'मासिक वेतन:',
        'Subsidized Canteen': 'किफायती कैंटीन',
        'Job A': 'नौकरी A',
        'Job B': 'नौकरी B',
        'Yes': 'हाँ',
        'No': 'नहीं',
        'Day': 'दिन',
        'Week': 'हफ़्ता',
        'Month': 'महीना',
    },
}

codings = {
    'wage_type' : {
        '0': 'Daily Wage:',
        '1': 'Weekly Wage',
        '2': 'Monthly Wage:',
    }
}

# Add variables to user's `profile` (created when `create_profile` route is called)
def add_to_profile(profile, **kwargs):
    # example: add timestamp to profile
    def generate_param_id(gender):
        if gender == 0:
            param_id = 0
        else:
            param_id = np.random.randint(1, 6)
        return param_id
    
    profile['timestamp'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    gender = int(profile['gender'])
    
    profile['param_id'] = generate_param_id(gender)

    profile['param'] = params[profile['param_id']]  
    profile['param_hi'] = translations['1'][profile['param']]
    return profile

def choice_message(profile, label, wage, design):

    # Get user's language from profile
    lang = profile.get('lang', '0')

    # Translate Params
    translated_param = translations[lang][profile['param']]

    # Determine the appropriate wage type translation
    wage_type = profile.get('wage_type', 'daily')  # Default to 'daily'
    wage_type_uncoded = codings['wage_type'][wage_type]
    translated_wage_type = translations[lang][wage_type_uncoded]

    # Translate Yes/No
    translated_design = translations[lang][design]

    # Translate label
    translated_label = translations[lang][label]

    wage = '₹{:,}'.format(int(wage))

    html_table = f"""
        <table width='300px' border='1' cellpadding='1' cellspacing='1' style='font-family: Arial, Tahoma, "Helvetica Neue", Helvetica, sans-serif; border-collapse:collapse; background-color:#eee9e7; color:black;'>
            <tbody>
                <tr>
                    <th style="text-align: center; background-color: #ded4ce;"><b>{translated_label}</b></th>
                </tr>
                <tr>
                    <td style="text-align: center;"><em>{translated_wage_type}</em><br> <b>{wage}</b></td>
                </tr>
                <tr>
                    <td style="text-align: center;"><em>{translated_param}:</em><br> <b>{translated_design}</b></td>
                </tr>
            </tbody>
        </table>
    """
    return html_table

def wage_dif(design,profile):

    wage_dif = abs(design['wage_a'] - design['wage_b'])
    wage_log_dif = abs(np.log(design['wage_a']) - np.log(design['wage_b']))
    round_log_dif = round(wage_log_dif, 2)
    
    if profile['lang'] == '0':
        return f"₹{wage_dif} ({round_log_dif:.0%})"
    else:
        return f"₹{wage_dif} ({round_log_dif:.0%})"    


def convert_design(design, profile, request_data, choice_message=choice_message,  **kwargs):

    # Number of questions
    Q = request_data.get('question_number') or len(profile.get('design_history'))

    output_design = {f'{key}_{Q}': value for key, value in design.items()}

    output_design[f'message_0_{Q}'] = choice_message(profile, "Job A", design['wage_a'], design['design_a'],)
    output_design[f'message_1_{Q}'] = choice_message(profile,"Job B", design['wage_b'], design['design_b'],)

    output_design[f'wage_dif_{Q}'] = wage_dif(design,profile)

    return output_design


