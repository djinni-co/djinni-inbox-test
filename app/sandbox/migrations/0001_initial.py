# Generated by Django 3.2 on 2023-11-03 11:47

from django.db import migrations, models
import django.db.models.deletion
import sandbox.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', null=True, max_length=255)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('picture_url', models.CharField(blank=True, default='', null=True, max_length=255)),
                ('position', models.CharField(default='', max_length=255)),
                ('primary_keyword', models.CharField(blank=True, db_index=True, default='', max_length=80)),
                ('secondary_keyword', models.CharField(blank=True, db_index=True, default='', max_length=80)),
                ('salary_min', models.IntegerField(blank=True, db_index=True, default=0)),
                ('employment', models.CharField(default='fulltime remote', max_length=80)),
                ('experience_years', models.FloatField(blank=True, default=0.0)),
                ('english_level', models.CharField(blank=True, choices=[('no_english', 'No English'), ('basic', 'Beginner/Elementary'), ('pre', 'Pre-Intermediate'), ('intermediate', 'Intermediate'), ('upper', 'Upper-Intermediate'), ('fluent', 'Advanced/Fluent')], default='', max_length=80)),
                ('skills_cache', models.TextField(blank=True, default='', null=True)),
                ('location', models.CharField(blank=True, default='', null=True, max_length=255)),
                ('country_code', models.CharField(blank=True, choices=[('AFG', 'Afghanistan'), ('ALB', 'Albania'), ('DZA', 'Algeria'), ('ASM', 'American Samoa'), ('AND', 'Andorra'), ('AGO', 'Angola'), ('AIA', 'Anguilla'), ('ATA', 'Antarctica'), ('ATG', 'Antigua and Barbuda'), ('ARG', 'Argentina'), ('ARM', 'Armenia'), ('ABW', 'Aruba'), ('AUS', 'Australia'), ('AUT', 'Austria'), ('AZE', 'Azerbaijan'), ('BHS', 'Bahamas'), ('BHR', 'Bahrain'), ('BGD', 'Bangladesh'), ('BRB', 'Barbados'), ('BLR', 'Belarus'), ('BEL', 'Belgium'), ('BLZ', 'Belize'), ('BEN', 'Benin'), ('BMU', 'Bermuda'), ('BTN', 'Bhutan'), ('BOL', 'Bolivia, Plurinational State of'), ('BES', 'Bonaire, Sint Eustatius and Saba'), ('BIH', 'Bosnia and Herzegovina'), ('BWA', 'Botswana'), ('BVT', 'Bouvet Island'), ('BRA', 'Brazil'), ('IOT', 'British Indian Ocean Territory'), ('BRN', 'Brunei Darussalam'), ('BGR', 'Bulgaria'), ('BFA', 'Burkina Faso'), ('BDI', 'Burundi'), ('CPV', 'Cabo Verde'), ('KHM', 'Cambodia'), ('CMR', 'Cameroon'), ('CAN', 'Canada'), ('CYM', 'Cayman Islands'), ('CAF', 'Central African Republic'), ('TCD', 'Chad'), ('CHL', 'Chile'), ('CHN', 'China'), ('CXR', 'Christmas Island'), ('CCK', 'Cocos (Keeling) Islands'), ('COL', 'Colombia'), ('COM', 'Comoros'), ('COG', 'Congo'), ('COD', 'Congo, The Democratic Republic of the'), ('COK', 'Cook Islands'), ('CRI', 'Costa Rica'), ('HRV', 'Croatia'), ('CUB', 'Cuba'), ('CUW', 'Curaçao'), ('CYP', 'Cyprus'), ('CZE', 'Czechia'), ('CIV', "Côte d'Ivoire"), ('DNK', 'Denmark'), ('DJI', 'Djibouti'), ('DMA', 'Dominica'), ('DOM', 'Dominican Republic'), ('ECU', 'Ecuador'), ('EGY', 'Egypt'), ('SLV', 'El Salvador'), ('GNQ', 'Equatorial Guinea'), ('ERI', 'Eritrea'), ('EST', 'Estonia'), ('SWZ', 'Eswatini'), ('ETH', 'Ethiopia'), ('FLK', 'Falkland Islands (Malvinas)'), ('FRO', 'Faroe Islands'), ('FJI', 'Fiji'), ('FIN', 'Finland'), ('FRA', 'France'), ('GUF', 'French Guiana'), ('PYF', 'French Polynesia'), ('ATF', 'French Southern Territories'), ('GAB', 'Gabon'), ('GMB', 'Gambia'), ('GEO', 'Georgia'), ('DEU', 'Germany'), ('GHA', 'Ghana'), ('GIB', 'Gibraltar'), ('GRC', 'Greece'), ('GRL', 'Greenland'), ('GRD', 'Grenada'), ('GLP', 'Guadeloupe'), ('GUM', 'Guam'), ('GTM', 'Guatemala'), ('GGY', 'Guernsey'), ('GIN', 'Guinea'), ('GNB', 'Guinea-Bissau'), ('GUY', 'Guyana'), ('HTI', 'Haiti'), ('HMD', 'Heard Island and McDonald Islands'), ('VAT', 'Holy See (Vatican City State)'), ('HND', 'Honduras'), ('HKG', 'Hong Kong'), ('HUN', 'Hungary'), ('ISL', 'Iceland'), ('IND', 'India'), ('IDN', 'Indonesia'), ('IRN', 'Iran, Islamic Republic of'), ('IRQ', 'Iraq'), ('IRL', 'Ireland'), ('IMN', 'Isle of Man'), ('ISR', 'Israel'), ('ITA', 'Italy'), ('JAM', 'Jamaica'), ('JPN', 'Japan'), ('JEY', 'Jersey'), ('JOR', 'Jordan'), ('KAZ', 'Kazakhstan'), ('KEN', 'Kenya'), ('KIR', 'Kiribati'), ('PRK', "Korea, Democratic People's Republic of"), ('KOR', 'Korea, Republic of'), ('KWT', 'Kuwait'), ('KGZ', 'Kyrgyzstan'), ('LAO', "Lao People's Democratic Republic"), ('LVA', 'Latvia'), ('LBN', 'Lebanon'), ('LSO', 'Lesotho'), ('LBR', 'Liberia'), ('LBY', 'Libya'), ('LIE', 'Liechtenstein'), ('LTU', 'Lithuania'), ('LUX', 'Luxembourg'), ('MAC', 'Macao'), ('MDG', 'Madagascar'), ('MWI', 'Malawi'), ('MYS', 'Malaysia'), ('MDV', 'Maldives'), ('MLI', 'Mali'), ('MLT', 'Malta'), ('MHL', 'Marshall Islands'), ('MTQ', 'Martinique'), ('MRT', 'Mauritania'), ('MUS', 'Mauritius'), ('MYT', 'Mayotte'), ('MEX', 'Mexico'), ('FSM', 'Micronesia, Federated States of'), ('MDA', 'Moldova, Republic of'), ('MCO', 'Monaco'), ('MNG', 'Mongolia'), ('MNE', 'Montenegro'), ('MSR', 'Montserrat'), ('MAR', 'Morocco'), ('MOZ', 'Mozambique'), ('MMR', 'Myanmar'), ('NAM', 'Namibia'), ('NRU', 'Nauru'), ('NPL', 'Nepal'), ('NLD', 'Netherlands'), ('NCL', 'New Caledonia'), ('NZL', 'New Zealand'), ('NIC', 'Nicaragua'), ('NER', 'Niger'), ('NGA', 'Nigeria'), ('NIU', 'Niue'), ('NFK', 'Norfolk Island'), ('MKD', 'North Macedonia'), ('MNP', 'Northern Mariana Islands'), ('NOR', 'Norway'), ('OMN', 'Oman'), ('PAK', 'Pakistan'), ('PLW', 'Palau'), ('PSE', 'Palestine, State of'), ('PAN', 'Panama'), ('PNG', 'Papua New Guinea'), ('PRY', 'Paraguay'), ('PER', 'Peru'), ('PHL', 'Philippines'), ('PCN', 'Pitcairn'), ('POL', 'Poland'), ('PRT', 'Portugal'), ('PRI', 'Puerto Rico'), ('QAT', 'Qatar'), ('ROU', 'Romania'), ('RUS', 'Russian Federation'), ('RWA', 'Rwanda'), ('REU', 'Réunion'), ('BLM', 'Saint Barthélemy'), ('SHN', 'Saint Helena, Ascension and Tristan da Cunha'), ('KNA', 'Saint Kitts and Nevis'), ('LCA', 'Saint Lucia'), ('MAF', 'Saint Martin (French part)'), ('SPM', 'Saint Pierre and Miquelon'), ('VCT', 'Saint Vincent and the Grenadines'), ('WSM', 'Samoa'), ('SMR', 'San Marino'), ('STP', 'Sao Tome and Principe'), ('SAU', 'Saudi Arabia'), ('SEN', 'Senegal'), ('SRB', 'Serbia'), ('SYC', 'Seychelles'), ('SLE', 'Sierra Leone'), ('SGP', 'Singapore'), ('SXM', 'Sint Maarten (Dutch part)'), ('SVK', 'Slovakia'), ('SVN', 'Slovenia'), ('SLB', 'Solomon Islands'), ('SOM', 'Somalia'), ('ZAF', 'South Africa'), ('SGS', 'South Georgia and the South Sandwich Islands'), ('SSD', 'South Sudan'), ('ESP', 'Spain'), ('LKA', 'Sri Lanka'), ('SDN', 'Sudan'), ('SUR', 'Suriname'), ('SJM', 'Svalbard and Jan Mayen'), ('SWE', 'Sweden'), ('CHE', 'Switzerland'), ('SYR', 'Syrian Arab Republic'), ('TWN', 'Taiwan, Province of China'), ('TJK', 'Tajikistan'), ('TZA', 'Tanzania, United Republic of'), ('THA', 'Thailand'), ('TLS', 'Timor-Leste'), ('TGO', 'Togo'), ('TKL', 'Tokelau'), ('TON', 'Tonga'), ('TTO', 'Trinidad and Tobago'), ('TUN', 'Tunisia'), ('TUR', 'Turkey'), ('TKM', 'Turkmenistan'), ('TCA', 'Turks and Caicos Islands'), ('TUV', 'Tuvalu'), ('UGA', 'Uganda'), ('UKR', 'Ukraine'), ('ARE', 'United Arab Emirates'), ('GBR', 'United Kingdom'), ('USA', 'United States'), ('UMI', 'United States Minor Outlying Islands'), ('URY', 'Uruguay'), ('UZB', 'Uzbekistan'), ('VUT', 'Vanuatu'), ('VEN', 'Venezuela, Bolivarian Republic of'), ('VNM', 'Viet Nam'), ('VGB', 'Virgin Islands, British'), ('VIR', 'Virgin Islands, U.S.'), ('WLF', 'Wallis and Futuna'), ('ESH', 'Western Sahara'), ('YEM', 'Yemen'), ('ZMB', 'Zambia'), ('ZWE', 'Zimbabwe'), ('ALA', 'Åland Islands')], db_index=True, default='', max_length=3)),
                ('city', models.CharField(blank=True, choices=[('Київ', 'Kyiv'), ('Вінниця', 'Vinnytsia'), ('Дніпро', 'Dnipro'), ('Івано-Франківськ', 'Ivano-Frankivsk'), ('Житомир', 'Zhytomyr'), ('Запоріжжя', 'Zaporizhzhia'), ('Львів', 'Lviv'), ('Миколаїв', 'Mykolaiv'), ('Одеса', 'Odesa'), ('Тернопіль', 'Ternopil'), ('Харків', 'Kharkiv'), ('Хмельницький', 'Khmelnytskyi'), ('Черкаси', 'Cherkasy'), ('Чернігів', 'Chernihiv'), ('Чернівці', 'Chernivtsi'), ('Ужгород', 'Uzhhorod')], db_index=True, default='', max_length=80, null=True)),
                ('can_relocate', models.BooleanField(default=False)),
                ('moreinfo', models.TextField(blank=True, default='', null=True)),
                ('looking_for', models.TextField(blank=True, default='', null=True)),
                ('highlights', models.TextField(blank=True, default='', null=True)),
                ('domain_zones', models.TextField(blank=True, default='', null=True)),
                ('uninterested_company_types', models.TextField(blank=True, default='', null=True)),
                ('question', models.TextField(blank=True, default='', null=True)),
                ('lang', models.CharField(blank=True, default='EN', max_length=10)),
                ('last_modified', models.DateTimeField(blank=True, null=True)),
                ('last_seen', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(default='', max_length=250)),
                ('primary_keyword', models.CharField(blank=True, default='', null=True, max_length=50)),
                ('secondary_keyword', models.CharField(blank=True, default='', null=True, max_length=50)),
                ('long_description', models.TextField(blank=True, default='', null=True)),
                ('extra_keywords', models.CharField(blank=True, default='', null=True, max_length=250)),
                ('location', models.CharField(blank=True, default='', null=True, max_length=250)),
                ('country', models.CharField(blank=True, default='', null=True, max_length=250)),
                ('salary_min', models.IntegerField(blank=True, default=0, null=True)),
                ('salary_max', models.IntegerField(blank=True, default=0, null=True)),
                ('exp_years', models.CharField(blank=True, choices=[('no_exp', 'No experience'), ('1y', '1 year'), ('2y', '2 years'), ('3y', '3 years'), ('5y', '5 years')], default='', max_length=10)),
                ('english_level', models.CharField(blank=True, choices=[('no_english', 'No English'), ('basic', 'Beginner/Elementary'), ('pre', 'Pre-Intermediate'), ('intermediate', 'Intermediate'), ('upper', 'Upper-Intermediate'), ('fluent', 'Advanced/Fluent')], default='', max_length=15)),
                ('domain', models.CharField(blank=True, default='', null=True, max_length=20)),
                ('is_parttime', models.BooleanField(db_index=True, default=False)),
                ('has_test', models.BooleanField(db_index=True, default=False)),
                ('requires_cover_letter', models.BooleanField(db_index=True, default=False)),
                ('is_ukraine_only', models.BooleanField(db_index=True, default=False)),
                ('accept_region', models.CharField(blank=True, choices=[(None, 'Worldwide'), ('europe', 'Ukraine + Europe'), ('europe_only', 'Only Europe'), ('ukraine', 'Only Ukraine')], default='', max_length=20)),
                ('company_type', models.CharField(blank=True, default='', null=True, max_length=20)),
                ('remote_type', models.CharField(blank=True, default='', null=True, max_length=20)),
                ('relocate_type', models.CharField(blank=True, choices=[('no_relocate', 'No relocation'), ('candidate_paid', 'Covered by candidate'), ('company_paid', 'Covered by company')], default='', max_length=20)),
                ('unread_count', models.IntegerField(default=0)),
                ('search_count', models.IntegerField(default=0)),
                ('views_count', models.IntegerField(default=0)),
                ('applications_count', models.IntegerField(default=0)),
                ('sent_count', models.IntegerField(default=0)),
                ('last_modified', models.DateTimeField(auto_now=True, db_index=True, null=True)),
                ('published', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(default='')),
                ('action', models.CharField(blank=True, choices=[('accept', 'Accept'), ('apply', 'Apply'), ('peek', 'Peek'), ('poke', 'Poke'), ('shadowpoke', 'Shadow Poke')], default='', max_length=40)),
                ('sender', models.CharField(choices=[('candidate', 'Candidate'), ('recruiter', 'Recruiter')], max_length=40)),
                ('created', models.DateTimeField(db_index=True)),
                ('notified', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('edited', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sandbox.candidate')),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sandbox.jobposting')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Recruiter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', null=True, max_length=255)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('picture_url', models.CharField(blank=True, default='', null=True, max_length=255)),
                ('lang', models.CharField(blank=True, default='EN', max_length=10)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('last_seen', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_anonymous', models.BooleanField(default=True)),
                ('iou_bonus', models.IntegerField(blank=True, default=0)),
                ('last_sender', models.CharField(choices=[('candidate', 'Candidate'), ('recruiter', 'Recruiter')], max_length=40)),
                ('first_message', models.CharField(choices=[('accept', 'Accept'), ('apply', 'Apply'), ('peek', 'Peek'), ('poke', 'Poke'), ('shadowpoke', 'Shadow Poke')], max_length=16)),
                ('bucket', models.CharField(db_index=True, default=sandbox.models.Bucket['INBOX'], max_length=40)),
                ('candidate_archived', models.BooleanField(blank=True, default=False)),
                ('candidate_favorite', models.BooleanField(blank=True, db_index=True, null=True)),
                ('feedback_candidate', models.CharField(blank=True, default='', null=True, max_length=20)),
                ('recruiter_favorite', models.BooleanField(blank=True, db_index=True, null=True)),
                ('feedback_recruiter', models.CharField(blank=True, default='', null=True, max_length=20)),
                ('notified_notinterested', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('last_updated', models.DateTimeField(db_index=True)),
                ('last_seen_recruiter', models.DateTimeField(null=True)),
                ('last_seen_candidate', models.DateTimeField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sandbox.candidate')),
                ('job', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sandbox.jobposting')),
                ('recruiter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sandbox.recruiter')),
            ],
            options={
                'ordering': ('-last_updated',),
                'unique_together': {('candidate', 'recruiter')},
            },
        ),
        migrations.AddField(
            model_name='message',
            name='recruiter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sandbox.recruiter'),
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sandbox.messagethread'),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='recruiter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sandbox.recruiter'),
        ),
    ]
