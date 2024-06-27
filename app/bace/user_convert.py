from datetime import datetime, timezone
import numpy as np

params = [
    'Maternity policy and related benefits',
    'Full Wages Paid on Time',
    'Wages Paid via Bank Account',
    'Pension Fund',
    'Health Insurance',
    'Appointment Letter + Pay Slip',
    'Safe Work Environment',
    'Guaranteed Employment for Entire Month',
    'Subsidized Canteen'
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
        'No': 'No'
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
        'No': 'नहीं'
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
    def generate_param_ids(gender):
        if gender == 0 and np.random.rand() < 0.5:
            param_id_1 = 0
        else:
            param_id_1 = np.random.randint(1, 9)
        while True:
            param_id_2 = np.random.randint(1, 9)
            if param_id_2 != param_id_1:
                break
        return param_id_1, param_id_2
    
    profile['timestamp'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    gender = int(profile['gender'])
    
    profile['param_id_1'], profile['param_id_2'] = generate_param_ids(gender)

    profile['param_1'] = params[profile['param_id_1']]
    profile['param_2'] = params[profile['param_id_2']]
    
    return profile

def choice_message(profile, label, wage, design_1, design_2):

    # Get user's language from profile
    lang = profile.get('lang', '0')

    # Translate Params
    translated_param_1 = translations[lang][profile['param_1']]
    translated_param_2 = translations[lang][profile['param_2']]

    # Determine the appropriate wage type translation
    wage_type = profile.get('wage_type', 'daily')  # Default to 'daily'
    wage_type_uncoded = codings['wage_type'][wage_type]
    translated_wage_type = translations[lang][wage_type_uncoded]

    # Translate Yes/No
    translated_design_1 = translations[lang][design_1]
    translated_design_2 = translations[lang][design_2]

    # Translate label
    translated_label = translations[lang][label]

    wage = '₹{:,} INR'.format(int(wage))

    html_table = f"""
        <table width='300px' border='1' cellpadding='1' cellspacing='1' style='font-family: Arial, Tahoma, "Helvetica Neue", Helvetica, sans-serif; border-collapse:collapse; background-color:#eee9e7; color:black;'>
            <tbody>
                <tr>
                    <th style="text-align: center; background-color: #ded4ce;"><b>{translated_label}</b></th>
                </tr>
                <tr>
                    <td style="text-align: center;"><em>{translated_wage_type}</em><br> {wage}</td>
                </tr>
                <tr>
                    <td style="text-align: center;"><em>{translated_param_1}:</em><br> {translated_design_1}</td>
                </tr>
                <tr>
                    <td style="text-align: center;"><em>{translated_param_2}:</em><br> {translated_design_2}</td>
                </tr>
            </tbody>
        </table>
    """
    return html_table

def convert_design(design, profile, request_data, choice_message=choice_message,  **kwargs):

    # Number of questions
    Q = request_data.get('question_number') or len(profile.get('design_history'))

    output_design = {f'{key}_{Q}': value for key, value in design.items()}

    output_design[f'message_0_{Q}'] = choice_message(profile, "Job A", design['wage_a'], design['design_1_a'], design['design_2_a'],)
    output_design[f'message_1_{Q}'] = choice_message(profile,"Job B", design['wage_b'], design['design_1_b'], design['design_2_b'],)

    return output_design
