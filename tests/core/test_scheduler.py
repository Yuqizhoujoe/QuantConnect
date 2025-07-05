"""
Tests for the Scheduler class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, time
from core.scheduler import Scheduler


class TestScheduler:
    """Test cases for Scheduler."""
    
    def test_initialization(self):
        """Test Scheduler initialization."""
        algorithm = Mock()
        
        scheduler = Scheduler(algorithm)
        
        assert scheduler.algorithm == algorithm
        assert scheduler.scheduled_tasks == []
        assert scheduler.last_execution == {}
    
    def test_add_task(self):
        """Test adding a task to the scheduler."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Mock task function
        task_func = Mock()
        
        # Add task
        scheduler.add_task("test_task", task_func, time(9, 30), "daily")
        
        # Should have one scheduled task
        assert len(scheduler.scheduled_tasks) == 1
        assert scheduler.scheduled_tasks[0]['name'] == "test_task"
        assert scheduler.scheduled_tasks[0]['function'] == task_func
        assert scheduler.scheduled_tasks[0]['time'] == time(9, 30)
        assert scheduler.scheduled_tasks[0]['frequency'] == "daily"
    
    def test_add_multiple_tasks(self):
        """Test adding multiple tasks to the scheduler."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Mock task functions
        task1 = Mock()
        task2 = Mock()
        
        # Add tasks
        scheduler.add_task("task1", task1, time(9, 30), "daily")
        scheduler.add_task("task2", task2, time(14, 0), "weekly")
        
        # Should have two scheduled tasks
        assert len(scheduler.scheduled_tasks) == 2
        assert scheduler.scheduled_tasks[0]['name'] == "task1"
        assert scheduler.scheduled_tasks[1]['name'] == "task2"
    
    def test_remove_task(self):
        """Test removing a task from the scheduler."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Mock task function
        task_func = Mock()
        
        # Add task
        scheduler.add_task("test_task", task_func, time(9, 30), "daily")
        assert len(scheduler.scheduled_tasks) == 1
        
        # Remove task
        scheduler.remove_task("test_task")
        assert len(scheduler.scheduled_tasks) == 0
    
    def test_remove_task_not_found(self):
        """Test removing a task that doesn't exist."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Try to remove non-existent task
        scheduler.remove_task("non_existent_task")
        
        # Should not raise an exception
        assert len(scheduler.scheduled_tasks) == 0
    
    def test_should_execute_task_daily_frequency(self):
        """Test daily task execution logic."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)  # Sunday 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'daily'
        }
        
        # Should execute if time matches and not executed today
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is True
    
    def test_should_execute_task_daily_already_executed(self):
        """Test daily task that was already executed today."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'daily'
        }
        
        # Mark as executed today
        scheduler.last_execution['test_task'] = datetime(2023, 1, 15, 9, 30, 0)
        
        # Should not execute again today
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_should_execute_task_daily_wrong_time(self):
        """Test daily task at wrong time."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 10, 0, 0)  # 10:00 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task scheduled for 9:30 AM
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'daily'
        }
        
        # Should not execute at wrong time
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_should_execute_task_weekly_frequency(self):
        """Test weekly task execution logic."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 16, 9, 30, 0)  # Monday 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'weekly'
        }
        
        # Should execute on Monday at correct time
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is True
    
    def test_should_execute_task_weekly_wrong_day(self):
        """Test weekly task on wrong day."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 17, 9, 30, 0)  # Tuesday 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'weekly'
        }
        
        # Should not execute on Tuesday (not Monday)
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_should_execute_task_monthly_frequency(self):
        """Test monthly task execution logic."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 1, 9, 30, 0)  # First day of month 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'monthly'
        }
        
        # Should execute on first day of month at correct time
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is True
    
    def test_should_execute_task_monthly_wrong_day(self):
        """Test monthly task on wrong day."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)  # 15th day of month 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'monthly'
        }
        
        # Should not execute on 15th day (not first day)
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_should_execute_task_unknown_frequency(self):
        """Test task with unknown frequency."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        
        scheduler = Scheduler(algorithm)
        
        # Mock task with unknown frequency
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'unknown'
        }
        
        # Should not execute with unknown frequency
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_execute_tasks_no_tasks(self):
        """Test executing tasks when no tasks are scheduled."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        
        scheduler = Scheduler(algorithm)
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Should not raise any exceptions
        assert len(scheduler.scheduled_tasks) == 0
    
    def test_execute_tasks_daily_task(self):
        """Test executing a daily task."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        
        scheduler = Scheduler(algorithm)
        
        # Mock task function
        task_func = Mock()
        
        # Add daily task
        scheduler.add_task("daily_task", task_func, time(9, 30), "daily")
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Task function should have been called
        task_func.assert_called_once()
        
        # Task should be marked as executed
        assert "daily_task" in scheduler.last_execution
    
    def test_execute_tasks_weekly_task(self):
        """Test executing a weekly task."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 16, 9, 30, 0)  # Monday 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task function
        task_func = Mock()
        
        # Add weekly task
        scheduler.add_task("weekly_task", task_func, time(9, 30), "weekly")
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Task function should have been called
        task_func.assert_called_once()
        
        # Task should be marked as executed
        assert "weekly_task" in scheduler.last_execution
    
    def test_execute_tasks_monthly_task(self):
        """Test executing a monthly task."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 1, 9, 30, 0)  # First day of month 9:30 AM
        
        scheduler = Scheduler(algorithm)
        
        # Mock task function
        task_func = Mock()
        
        # Add monthly task
        scheduler.add_task("monthly_task", task_func, time(9, 30), "monthly")
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Task function should have been called
        task_func.assert_called_once()
        
        # Task should be marked as executed
        assert "monthly_task" in scheduler.last_execution
    
    def test_execute_tasks_multiple_tasks(self):
        """Test executing multiple tasks."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        
        scheduler = Scheduler(algorithm)
        
        # Mock task functions
        task1 = Mock()
        task2 = Mock()
        
        # Add tasks
        scheduler.add_task("task1", task1, time(9, 30), "daily")
        scheduler.add_task("task2", task2, time(9, 30), "daily")
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Both task functions should have been called
        task1.assert_called_once()
        task2.assert_called_once()
        
        # Both tasks should be marked as executed
        assert "task1" in scheduler.last_execution
        assert "task2" in scheduler.last_execution
    
    def test_execute_tasks_task_exception(self):
        """Test executing tasks when a task raises an exception."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)
        algorithm.Log = Mock()
        
        scheduler = Scheduler(algorithm)
        
        # Mock task function that raises an exception
        def failing_task():
            raise Exception("Task failed")
        
        # Add failing task
        scheduler.add_task("failing_task", failing_task, time(9, 30), "daily")
        
        # Execute tasks
        scheduler.execute_tasks()
        
        # Should log the error
        algorithm.Log.assert_called()
        assert "Error executing task" in str(algorithm.Log.call_args)
    
    def test_get_scheduled_tasks(self):
        """Test getting list of scheduled tasks."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Mock task functions
        task1 = Mock()
        task2 = Mock()
        
        # Add tasks
        scheduler.add_task("task1", task1, time(9, 30), "daily")
        scheduler.add_task("task2", task2, time(14, 0), "weekly")
        
        # Get scheduled tasks
        tasks = scheduler.get_scheduled_tasks()
        
        # Should return list of task names
        assert len(tasks) == 2
        assert "task1" in tasks
        assert "task2" in tasks
    
    def test_clear_all_tasks(self):
        """Test clearing all scheduled tasks."""
        algorithm = Mock()
        scheduler = Scheduler(algorithm)
        
        # Mock task functions
        task1 = Mock()
        task2 = Mock()
        
        # Add tasks
        scheduler.add_task("task1", task1, time(9, 30), "daily")
        scheduler.add_task("task2", task2, time(14, 0), "weekly")
        
        # Clear all tasks
        scheduler.clear_all_tasks()
        
        # Should have no scheduled tasks
        assert len(scheduler.scheduled_tasks) == 0
        assert len(scheduler.last_execution) == 0
    
    def test_task_execution_timing_edge_case(self):
        """Test task execution timing edge case."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 1)  # 1 second after scheduled time
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'daily'
        }
        
        # Should not execute if time has passed
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is False
    
    def test_task_execution_timing_within_window(self):
        """Test task execution within time window."""
        algorithm = Mock()
        algorithm.Time = datetime(2023, 1, 15, 9, 30, 0)  # Exactly at scheduled time
        
        scheduler = Scheduler(algorithm)
        
        # Mock task
        task = {
            'name': 'test_task',
            'function': Mock(),
            'time': time(9, 30),
            'frequency': 'daily'
        }
        
        # Should execute at exact time
        should_execute = scheduler._should_execute_task(task)
        assert should_execute is True 