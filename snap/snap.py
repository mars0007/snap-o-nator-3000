import boto3
import botocore
import click

# aws connection setup for your default account
session = boto3.Session(profile_name='default') 
ec2 = session.resource('ec2') 

# common functions used in the script
# this function will filter instance with the project tag.
def filter_instances_noforce(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
        
    return instances
# this function will filter instance with the project tag, it will also look for the force switch and exit if it isn't provided. 
def filter_instances(project, force=False):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        if force:
            instances = ec2.instances.all()
        else:
            print('project not set, exiting...')
            exit()

    return instances
# looks for pending snapshots
def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

# cli
@click.group()
def cli():
    """snap manages snapshots"""

# snapshot commands
@cli.group('snapshots')
def snapshots():
    """Commands for snapshorts"""
# snapshot list
@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots not only the most recent")    
def list_snapshots(project,list_all):
    "List EC2 snapshots"
    
    instances = filter_instances_noforce(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break
    
    return

# volume commands
@cli.group('volumes')
def volumes():
    """Commands for volumes"""
# volume list
@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"
    
    instances = filter_instances_noforce(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                v.state,
                i.id,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

# instance commands
@cli.group('instances')
def instances():
    """Commands for instances"""
# instance list
@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances_noforce(project)
        
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))
            

    return
# instance snapshot
@instances.command('snapshot',
    help="Create snapshot of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True,
    help="Forces execution even without the project tag")
def create_snapshots(project,force):
    """Create snapshot for EC2 instances"""

    instances = filter_instances(project,force)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()
        
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("  Skipping {0}, snapshot alrady in progress".format(v.id))
                continue
            print("  Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by snap.py")

        print("Starting {0}...".format(i.id))  

        i.start()
        i.wait_until_running()
    
    print("Snapshot taken, instances restarted, JOB DONE!")

    return
# instance stop
@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True,
    help="Forces execution even without the project tag")
def stop_instances(project, force):
    "Stop EC2 instances"
    
    instances = filter_instances(project,force)
    
    for i in instances:
        print('Stopping {0}...'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print(" Could not stop {0}. ".format(i.id) + str(e))
            continue

    return
# instance start
@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True,
    help="Forces execution even without the project tag")
def stop_instances(project, force):
    "Start EC2 instances"
    
    instances = filter_instances(project,force)
    
    for i in instances:
        print('Starting {0}...'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print(" Could not start {0}. ".format(i.id) + str(e))
            continue

    return
# instance reboot
@instances.command('reboot')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True,
    help="Forces execution even without the project tag")
def reboot_instances(project, force):
    "Reboot EC2 instances"
    
    instances = filter_instances(project,force)
    
    for i in instances:
        print('Rebooting {0}...'.format(i.id))
        try:
            i.reboot()
        except botocore.exceptions.ClientError as e:
            print(" Could not reboot {0}. ".format(i.id) + str(e))
            continue

    return

# main
if __name__ == '__main__':
    cli()
