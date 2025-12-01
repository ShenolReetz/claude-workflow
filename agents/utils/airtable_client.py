"""
Airtable Client Helper
=======================
Provides a simple interface for agents to interact with Airtable.
Uses pyairtable library for direct API access.
"""

import logging
from typing import Dict, Any, List, Optional
from pyairtable import Api, Base, Table


class AirtableClient:
    """
    Airtable client wrapper for agent use.

    Usage:
        client = AirtableClient(api_key, base_id, table_id)
        records = await client.list_records(filter_by_formula="Status = 'Pending'")
        await client.update_record(record_id, {'Status': 'Processing'})
    """

    def __init__(self, api_key: str, base_id: str, table_id: str):
        """
        Initialize Airtable client

        Args:
            api_key: Airtable API key
            base_id: Base ID (e.g., 'appTtNBJ8dAnjvkPP')
            table_id: Table ID (e.g., 'tblhGDEW6eUbmaYZx')
        """
        self.api_key = api_key
        self.base_id = base_id
        self.table_id = table_id

        # Initialize pyairtable
        self.api = Api(api_key)
        self.table = self.api.table(base_id, table_id)

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"✅ AirtableClient initialized: {base_id}/{table_id}")

    def list_records(
        self,
        formula: Optional[str] = None,
        max_records: Optional[int] = None,
        sort: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List records from Airtable

        Args:
            formula: Filter formula (e.g., "Status = 'Pending'")
            max_records: Maximum number of records to return
            sort: List of field names (prefix with '-' for descending, e.g., ['-ID'] or ['ID'])
            fields: List of field names to return

        Returns:
            List of records with 'id' and 'fields' keys
        """
        try:
            kwargs = {}
            if formula:
                kwargs['formula'] = formula
            if max_records:
                kwargs['max_records'] = max_records
            if sort:
                # pyairtable expects list of field names, with '-' prefix for desc
                kwargs['sort'] = sort
            if fields:
                kwargs['fields'] = fields

            records = self.table.all(**kwargs)

            self.logger.info(f"📥 Fetched {len(records)} records from Airtable")
            return records

        except Exception as e:
            self.logger.error(f"❌ Failed to list records: {e}")
            raise

    def get_record(self, record_id: str) -> Dict[str, Any]:
        """
        Get a single record by ID

        Args:
            record_id: Airtable record ID

        Returns:
            Record dict with 'id' and 'fields' keys
        """
        try:
            record = self.table.get(record_id)
            self.logger.info(f"📥 Fetched record: {record_id}")
            return record

        except Exception as e:
            self.logger.error(f"❌ Failed to get record {record_id}: {e}")
            raise

    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a single record

        Args:
            record_id: Airtable record ID
            fields: Dictionary of fields to update

        Returns:
            Updated record
        """
        try:
            record = self.table.update(record_id, fields)
            self.logger.info(f"✅ Updated record: {record_id} ({len(fields)} fields)")
            return record

        except Exception as e:
            self.logger.error(f"❌ Failed to update record {record_id}: {e}")
            raise

    def update_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple records in batch

        Args:
            records: List of dicts with 'id' and 'fields' keys

        Returns:
            List of updated records
        """
        try:
            updated = self.table.batch_update(records)
            self.logger.info(f"✅ Updated {len(updated)} records in batch")
            return updated

        except Exception as e:
            self.logger.error(f"❌ Failed to batch update records: {e}")
            raise

    def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record

        Args:
            fields: Dictionary of fields for new record

        Returns:
            Created record
        """
        try:
            record = self.table.create(fields)
            self.logger.info(f"✅ Created new record: {record['id']}")
            return record

        except Exception as e:
            self.logger.error(f"❌ Failed to create record: {e}")
            raise

    def search_records(
        self,
        field_name: str,
        field_value: Any,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for records by field value

        Args:
            field_name: Name of field to search
            field_value: Value to search for
            max_records: Maximum number of results

        Returns:
            List of matching records
        """
        try:
            # Build filter formula
            if isinstance(field_value, str):
                formula = f"{{{field_name}}} = '{field_value}'"
            else:
                formula = f"{{{field_name}}} = {field_value}"

            return self.list_records(formula=formula, max_records=max_records)

        except Exception as e:
            self.logger.error(f"❌ Failed to search records: {e}")
            raise
