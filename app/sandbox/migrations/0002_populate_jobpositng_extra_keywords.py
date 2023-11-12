# Generated by Django 3.2.23 on 2023-11-11 19:36

from django.db import migrations


def populate_jobposting_keywords(apps, schema_editor):
    JobPosting = apps.get_model('sandbox', 'JobPosting')
    for job in JobPosting.objects.filter(primary_keyword__in=['JavaScript', 'Node.js']):
        job.extra_keywords = 'React/Redux/Next.js\nReact Native\nReact.js\nNode.js\nNode.js + Express.js\nJavaScript / NodeJS\nMongoose\nReact\nCSS\nHTML\nTypeScript\nJavaScript'
        job.save(update_fields=['extra_keywords'])
    for job in JobPosting.objects.filter(primary_keyword='Data Analyst'):
        job.extra_keywords = 'Machine Learning\nData Science\nPandas\nPython\nGoogle Analytics\nData Visualisation\nStatistics\nnumpy'
        job.save(update_fields=['extra_keywords'])
    for job in JobPosting.objects.filter(primary_keyword='Golang'):
        job.extra_keywords = 'Golang\nOOP\nREST API\nDesign Patterns\nDocker / Docker Compose\nGit\nWebSockets\nPostgreSQL\nAWS\nGoLang / Go\nGo\nCI/CD\nDocker'
        job.save(update_fields=['extra_keywords'])
    for job in JobPosting.objects.filter(primary_keyword='Marketing'):
        job.extra_keywords = 'digital marketing\nmarketing\nSMM\nSEO\nlead generation\nGoogle Ads\nFacebook Ads\nGoogle Analytics\nSocial Media Marketing'
        job.save(update_fields=["extra_keywords"])


def revert_jobposting_keywords(apps, schema_editor):
    JobPosting = apps.get_model("sandbox", "JobPosting")
    JobPosting.objects.update(extra_keywords='')


class Migration(migrations.Migration):

    dependencies = [
        ('sandbox', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_jobposting_keywords, revert_jobposting_keywords),
    ]
