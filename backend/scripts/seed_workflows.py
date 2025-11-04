#!/usr/bin/env python3
"""
Seed workflows with plant associations and phases
Creates sample workflows linked to existing plants
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.workflow import Workflow, WorkflowPhase, WorkflowStatusEnum, WorkflowTypeEnum
from app.models.plant import Plant
from app.models.user import User
from datetime import datetime, timedelta
import random

def seed_workflows():
    """Create sample workflows with plant associations and phases"""
    db: Session = next(get_db())
    
    try:
        # Get demo tenant
        tenant_id = "demo"
        
        # Get a user for created_by
        user = db.query(User).filter(User.tenant_id == tenant_id).first()
        if not user:
            print("❌ No user found for tenant 'demo'. Please seed users first.")
            return
        
        # Get all plants for the tenant
        plants = db.query(Plant).filter(
            Plant.tenant_id == tenant_id,
            Plant.deleted_at.is_(None)
        ).all()
        
        if not plants:
            print("❌ No plants found for tenant 'demo'. Please seed plants first.")
            return
        
        print(f"✅ Found {len(plants)} plants to associate workflows with")
        
        # Define workflow templates with phases
        workflow_templates = [
            {
                "name": "Complete Plant Activation",
                "description": "Complete activation process for renewable energy plant",
                "type": WorkflowTypeEnum.ACTIVATION,
                "phases": [
                    {
                        "name": "DSO Connection Request",
                        "description": "Submit connection request to Distribution System Operator",
                        "order": 1,
                        "status": "completed",
                        "estimated_days": 30,
                    },
                    {
                        "name": "TICA Acceptance",
                        "description": "Review and accept Technical Connection Agreement",
                        "order": 2,
                        "status": "in_progress",
                        "estimated_days": 15,
                    },
                    {
                        "name": "GAUDÌ Registration",
                        "description": "Register plant with Terna GAUDÌ portal",
                        "order": 3,
                        "status": "pending",
                        "estimated_days": 20,
                    },
                    {
                        "name": "GSE RID Activation",
                        "description": "Activate Ritiro Dedicato contract with GSE",
                        "order": 4,
                        "status": "pending",
                        "estimated_days": 30,
                    },
                    {
                        "name": "ADM License Application",
                        "description": "Apply for UTF license with Customs Agency (if >20kW)",
                        "order": 5,
                        "status": "pending",
                        "estimated_days": 15,
                    },
                ]
            },
            {
                "name": "Annual Compliance Review",
                "description": "Annual compliance obligations and renewals",
                "type": WorkflowTypeEnum.COMPLIANCE,
                "phases": [
                    {
                        "name": "Fuel Mix Disclosure",
                        "description": "Submit annual fuel mix disclosure to GSE",
                        "order": 1,
                        "status": "pending",
                        "estimated_days": 7,
                    },
                    {
                        "name": "Consumption Declaration",
                        "description": "Submit consumption declaration to ADM",
                        "order": 2,
                        "status": "pending",
                        "estimated_days": 7,
                    },
                    {
                        "name": "Anti-Mafia Declaration",
                        "description": "Submit anti-mafia declaration (if required)",
                        "order": 3,
                        "status": "pending",
                        "estimated_days": 5,
                    },
                ]
            },
            {
                "name": "Meter Calibration Renewal",
                "description": "Renew meter calibration certificate",
                "type": WorkflowTypeEnum.MAINTENANCE,
                "phases": [
                    {
                        "name": "Schedule Calibration",
                        "description": "Schedule calibration appointment with DSO",
                        "order": 1,
                        "status": "in_progress",
                        "estimated_days": 10,
                    },
                    {
                        "name": "Perform Calibration",
                        "description": "Execute meter calibration test",
                        "order": 2,
                        "status": "pending",
                        "estimated_days": 1,
                    },
                    {
                        "name": "Receive Certificate",
                        "description": "Receive and archive calibration certificate",
                        "order": 3,
                        "status": "pending",
                        "estimated_days": 5,
                    },
                ]
            },
            {
                "name": "License Fee Payment",
                "description": "Annual license fee payment to ADM",
                "type": WorkflowTypeEnum.FISCAL,
                "phases": [
                    {
                        "name": "Calculate Fee",
                        "description": "Calculate license fee based on plant power",
                        "order": 1,
                        "status": "completed",
                        "estimated_days": 2,
                    },
                    {
                        "name": "Process Payment",
                        "description": "Process payment through ADM portal",
                        "order": 2,
                        "status": "in_progress",
                        "estimated_days": 3,
                    },
                    {
                        "name": "Confirmation",
                        "description": "Receive payment confirmation",
                        "order": 3,
                        "status": "pending",
                        "estimated_days": 2,
                    },
                ]
            },
            {
                "name": "Document Submission - GSE",
                "description": "Submit required documents to GSE portal",
                "type": WorkflowTypeEnum.DOCUMENT_SUBMISSION,
                "phases": [
                    {
                        "name": "Gather Documents",
                        "description": "Collect all required documents",
                        "order": 1,
                        "status": "completed",
                        "estimated_days": 5,
                    },
                    {
                        "name": "Upload to Portal",
                        "description": "Upload documents via GSE portal",
                        "order": 2,
                        "status": "in_progress",
                        "estimated_days": 2,
                    },
                    {
                        "name": "Verification",
                        "description": "Wait for GSE verification",
                        "order": 3,
                        "status": "pending",
                        "estimated_days": 10,
                    },
                ]
            },
        ]
        
        # Create workflows for each plant
        created_workflows = []
        status_distribution = [
            WorkflowStatusEnum.IN_PROGRESS,
            WorkflowStatusEnum.IN_PROGRESS,
            WorkflowStatusEnum.DRAFT,
            WorkflowStatusEnum.ON_HOLD,
            WorkflowStatusEnum.COMPLETED,
        ]
        
        for plant in plants:
            # Create 2-3 workflows per plant
            num_workflows = random.randint(2, 3)
            selected_templates = random.sample(workflow_templates, num_workflows)
            
            for template in selected_templates:
                # Check if workflow already exists
                existing = db.query(Workflow).filter(
                    Workflow.tenant_id == tenant_id,
                    Workflow.plant_id == plant.id,
                    Workflow.name == template["name"],
                    Workflow.deleted_at.is_(None)
                ).first()
                
                if existing:
                    print(f"ℹ️  Workflow '{template['name']}' for plant '{plant.name}' already exists")
                    continue
                
                # Determine status and dates
                status = random.choice(status_distribution)
                start_date = datetime.utcnow() - timedelta(days=random.randint(0, 60))
                
                if status == WorkflowStatusEnum.COMPLETED:
                    due_date = start_date + timedelta(days=random.randint(30, 90))
                    completed_date = due_date + timedelta(days=random.randint(-5, 5))
                    progress = 100
                elif status == WorkflowStatusEnum.IN_PROGRESS:
                    due_date = datetime.utcnow() + timedelta(days=random.randint(7, 60))
                    completed_date = None
                    progress = random.randint(20, 80)
                else:
                    due_date = datetime.utcnow() + timedelta(days=random.randint(30, 120))
                    completed_date = None
                    progress = random.randint(0, 20)
                
                # Create workflow
                workflow = Workflow(
                    tenant_id=tenant_id,
                    name=f"{template['name']} - {plant.name}",
                    description=template["description"],
                    type=template["type"],
                    status=status,
                    plant_id=plant.id,
                    start_date=start_date,
                    due_date=due_date,
                    completed_date=completed_date,
                    progress_percentage=progress,
                    current_phase=template["phases"][min(1, len(template["phases"]) - 1)]["name"] if template["phases"] else None,
                    created_by=user.id,
                )
                
                db.add(workflow)
                db.flush()
                
                # Create phases
                phase_order = 0
                completed_phases = 0
                for phase_template in template["phases"]:
                    phase_order += 1
                    phase_status = phase_template["status"]
                    
                    # Calculate phase dates based on workflow dates
                    phase_start = start_date + timedelta(days=sum(p["estimated_days"] for p in template["phases"][:phase_order-1]))
                    phase_due = phase_start + timedelta(days=phase_template["estimated_days"])
                    
                    if phase_status == "completed":
                        phase_completed = phase_due + timedelta(days=random.randint(-2, 2))
                        completed_phases += 1
                    elif phase_status == "in_progress":
                        phase_completed = None
                        completed_phases += 0.5
                    else:
                        phase_completed = None
                    
                    phase = WorkflowPhase(
                        tenant_id=tenant_id,
                        workflow_id=workflow.id,
                        name=phase_template["name"],
                        description=phase_template["description"],
                        order=phase_template["order"],
                        status=phase_status,
                        due_date=phase_due,
                        completed_date=phase_completed,
                        phase_data={
                            "estimated_days": phase_template["estimated_days"],
                        },
                        created_by=user.id,
                    )
                    db.add(phase)
                
                created_workflows.append(workflow)
                print(f"✅ Created workflow '{workflow.name}' for plant '{plant.name}' with {len(template['phases'])} phases")
        
        db.commit()
        
        print("\n" + "="*60)
        print("🎉 Workflow seeding completed!")
        print("="*60)
        print(f"✅ Created {len(created_workflows)} workflows")
        print(f"✅ Associated with {len(plants)} plants")
        print(f"✅ Average {len(created_workflows) / len(plants):.1f} workflows per plant")
        print("\n💡 Workflows are now linked to plants and include phases!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_workflows()

