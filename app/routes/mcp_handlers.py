"""
MCP tool call handlers.

These functions handle individual tool calls within the MCP protocol.
Separated from the main MCP route for better organization.
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, Callable

from memory.mcp_client import MCPClient
from integrations.google_calendar import get_google_calendar_client
from integrations.google_sheets import get_google_sheets_client
from integrations.browser import get_browser_service


def handle_search_knowledge_base(
    mcp: MCPClient,
    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle search_knowledge_base tool call."""
    try:
        query = arguments.get("query", "")
        k = arguments.get("k", 4)
        results = mcp.retrieve(query, k=k)
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.get("page_content", ""),
                "metadata": doc.get("metadata", {}),
                "title": doc.get("metadata", {}).get("title") or doc.get("metadata", {}).get("source", "Document")
            })
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(formatted_results)} results for query: {query}\n\n" + 
                           "\n\n".join([f"**{r['title']}**\n{r['content'][:500]}" for r in formatted_results])
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error searching knowledge base: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_create_ticket(
    crm: Any,

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle create_support_ticket tool call."""
    try:
        crm = request.app.state.crm
        title = arguments.get("title", "")
        description = arguments.get("description", "")
        if not crm:
            ticket_id = f"ticket_{int(time.time())}"
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Ticket created: {ticket_id}. Status: created. CRM not configured - ticket created in mock mode"
                    }
                ]
            })
        result = crm.create_ticket(
            title=title,
            description=description,
            customer_id=arguments.get("customer_id"),
            priority=arguments.get("priority", "normal"),
            tags=arguments.get("tags", [])
        )
        ticket_id = result.get("id", "unknown")
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Ticket created: {ticket_id}. Status: {result.get('status', 'created')}. Ticket created successfully"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error creating ticket: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_get_customer(
    crm: Any,

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle get_customer_info tool call."""
    try:
        crm = request.app.state.crm
        identifier = arguments.get("identifier", "")
        if not crm:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"CRM not configured. Mock customer info for {identifier}: Customer ID: {identifier}, Status: active, Orders: 0"
                    }
                ]
            })
        customer = crm.get_customer(identifier)
        if not customer:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Customer not found: {identifier}"
                    }
                ]
            })
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Customer found: {customer.get('id', identifier)}, Name: {customer.get('name', 'Unknown')}, Email: {customer.get('email', 'N/A')}"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error retrieving customer: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_escalate(
    escalations: Any,

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle escalate_to_human tool call."""
    try:
        escalations = request.app.state.escalations
        session_id = arguments.get("session_id", "")
        reason = arguments.get("reason", "user_request")
        escalations.update_escalation(session_id, {"status": "escalated", "reason": reason})
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Conversation escalated to human agent. Session: {session_id}, Reason: {reason}"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error escalating conversation: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_log_interaction(
    crm: Any,

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle log_interaction tool call."""
    try:
        crm = request.app.state.crm
        customer_id = arguments.get("customer_id", "")
        activity_type = arguments.get("activity_type", "")
        details = arguments.get("details", {})
        if not crm:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"CRM not configured. Interaction logged in mock mode: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
        success = crm.log_interaction(customer_id, activity_type, details)
        if success:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Interaction logged successfully: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Failed to log interaction: Customer: {customer_id}, Type: {activity_type}"
                    }
                ]
            })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error logging interaction: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_check_order(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle check_order_status tool call."""
    try:
        order_id = arguments.get("order_id", "")
        # Mock implementation - in production, this would query an order system
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Order {order_id}: Status: processing, Estimated delivery: 3-5 business days. (Mock response - order system not integrated)"
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error checking order status: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_check_availability(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle check_availability tool call."""
    try:
        calendar_client = get_google_calendar_client()
        if not calendar_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Calendar not configured. Please configure GOOGLE_CALENDAR_CREDENTIALS_PATH and GOOGLE_CALENDAR_TOKEN_PATH"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        # Parse time parameters
        time_min = None
        time_max = None
        if arguments.get("time_min"):
            time_min = datetime.fromisoformat(arguments["time_min"].replace('Z', '+00:00'))
        if arguments.get("time_max"):
            time_max = datetime.fromisoformat(arguments["time_max"].replace('Z', '+00:00'))
        
        duration_minutes = arguments.get("duration_minutes", 30)
        
        result = calendar_client.check_availability(
            time_min=time_min,
            time_max=time_max,
            duration_minutes=duration_minutes
        )
        
        if result.get("error"):
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result["error"]
                    }
                ],
                "isError": True
            }, is_error=True)
        
        # Format response
        available_slots = result.get("available_slots", [])
        events = result.get("events", [])
        
        response_text = f"Availability check: {result.get('summary', '')}\n\n"
        response_text += f"Found {len(available_slots)} available slots:\n"
        for i, slot in enumerate(available_slots[:10], 1):  # Show first 10
            response_text += f"{i}. {slot.get('start')} - {slot.get('end')} ({slot.get('duration_minutes')} min)\n"
        
        if len(available_slots) > 10:
            response_text += f"\n... and {len(available_slots) - 10} more slots\n"
        
        if events:
            response_text += f"\nExisting events: {len(events)}\n"
            for event in events[:5]:  # Show first 5
                response_text += f"- {event.get('summary')} ({event.get('start')})\n"
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error checking availability: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_get_user_bookings(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle getUserBookings tool call."""
    try:
        calendar_client = get_google_calendar_client()
        if not calendar_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Calendar not configured. Please configure GOOGLE_CALENDAR_CREDENTIALS_PATH and GOOGLE_CALENDAR_TOKEN_PATH"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        # Parse time parameters
        time_min = None
        time_max = None
        if arguments.get("time_min"):
            time_min = datetime.fromisoformat(arguments["time_min"].replace('Z', '+00:00'))
        if arguments.get("time_max"):
            time_max = datetime.fromisoformat(arguments["time_max"].replace('Z', '+00:00'))
        
        max_results = arguments.get("max_results", 50)
        
        result = calendar_client.get_user_bookings(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        if result.get("error"):
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result["error"]
                    }
                ],
                "isError": True
            }, is_error=True)
        
        bookings = result.get("bookings", [])
        response_text = f"User bookings: {result.get('summary', '')}\n\n"
        
        if not bookings:
            response_text += "No bookings found in the specified time range."
        else:
            for i, booking in enumerate(bookings, 1):
                response_text += f"{i}. {booking.get('summary')}\n"
                response_text += f"   Start: {booking.get('start')}\n"
                response_text += f"   End: {booking.get('end')}\n"
                if booking.get('location'):
                    response_text += f"   Location: {booking.get('location')}\n"
                response_text += "\n"
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error getting user bookings: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_book_appointment(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle bookAppointment tool call."""
    try:
        calendar_client = get_google_calendar_client()
        if not calendar_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Calendar not configured. Please configure GOOGLE_CALENDAR_CREDENTIALS_PATH and GOOGLE_CALENDAR_TOKEN_PATH"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        summary = arguments.get("summary", "")
        if not summary:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'summary' is required for booking an appointment"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        # Parse datetime strings
        start_time_str = arguments.get("start_time", "")
        end_time_str = arguments.get("end_time", "")
        
        if not start_time_str or not end_time_str:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'start_time' and 'end_time' are required (ISO format)"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        
        result = calendar_client.book_appointment(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=arguments.get("description"),
            location=arguments.get("location"),
            attendees=arguments.get("attendees", [])
        )
        
        if result.get("success"):
            response_text = f"✅ {result.get('message', 'Appointment booked successfully')}\n"
            response_text += f"Event ID: {result.get('event_id')}\n"
            response_text += f"Start: {result.get('start')}\n"
            response_text += f"End: {result.get('end')}\n"
            if result.get("html_link"):
                response_text += f"Calendar link: {result.get('html_link')}\n"
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Failed to book appointment")
                    }
                ],
                "isError": True
            }, is_error=True)
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error booking appointment: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_modify_appointment(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle modifyAppointment tool call."""
    try:
        calendar_client = get_google_calendar_client()
        if not calendar_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Calendar not configured. Please configure GOOGLE_CALENDAR_CREDENTIALS_PATH and GOOGLE_CALENDAR_TOKEN_PATH"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        event_id = arguments.get("event_id", "")
        if not event_id:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'event_id' is required for modifying an appointment"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        # Parse optional datetime strings
        start_time = None
        end_time = None
        if arguments.get("start_time"):
            start_time = datetime.fromisoformat(arguments["start_time"].replace('Z', '+00:00'))
        if arguments.get("end_time"):
            end_time = datetime.fromisoformat(arguments["end_time"].replace('Z', '+00:00'))
        
        result = calendar_client.modify_appointment(
            event_id=event_id,
            summary=arguments.get("summary"),
            start_time=start_time,
            end_time=end_time,
            description=arguments.get("description"),
            location=arguments.get("location"),
            attendees=arguments.get("attendees")
        )
        
        if result.get("success"):
            response_text = f"✅ {result.get('message', 'Appointment modified successfully')}\n"
            response_text += f"Event ID: {result.get('event_id')}\n"
            response_text += f"Start: {result.get('start')}\n"
            response_text += f"End: {result.get('end')}\n"
            if result.get("html_link"):
                response_text += f"Calendar link: {result.get('html_link')}\n"
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Failed to modify appointment")
                    }
                ],
                "isError": True
            }, is_error=True)
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error modifying appointment: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_cancel_appointment(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle cancelAppointment tool call."""
    try:
        calendar_client = get_google_calendar_client()
        if not calendar_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Calendar not configured. Please configure GOOGLE_CALENDAR_CREDENTIALS_PATH and GOOGLE_CALENDAR_TOKEN_PATH"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        event_id = arguments.get("event_id", "")
        if not event_id:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'event_id' is required for cancelling an appointment"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        result = calendar_client.cancel_appointment(event_id=event_id)
        
        if result.get("success"):
            response_text = f"✅ {result.get('message', 'Appointment cancelled successfully')}\n"
            response_text += f"Event ID: {result.get('event_id')}\n"
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Failed to cancel appointment")
                    }
                ],
                "isError": True
            }, is_error=True)
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error cancelling appointment: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_post_call_data(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle postCallData tool call."""
    try:
        sheets_client = get_google_sheets_client()
        if not sheets_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Sheets not configured. Please configure GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_TOKEN_PATH, and GOOGLE_SHEETS_SPREADSHEET_ID"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        call_data = arguments.get("call_data", {})
        if not call_data:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'call_data' is required (object with call information)"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        sheet_name = arguments.get("sheet_name")
        
        result = sheets_client.post_call_data(
            call_data=call_data,
            sheet_name=sheet_name
        )
        
        if result.get("success"):
            response_text = f"✅ {result.get('message', 'Call data posted successfully')}"
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Failed to post call data")
                    }
                ],
                "isError": True
            }, is_error=True)
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error posting call data: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_get_clients(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle getClients tool call."""
    try:
        sheets_client = get_google_sheets_client()
        if not sheets_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Sheets not configured. Please configure GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_TOKEN_PATH, and GOOGLE_SHEETS_SPREADSHEET_ID"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        sheet_name = arguments.get("sheet_name")
        range_name = arguments.get("range_name")
        
        result = sheets_client.get_clients(
            sheet_name=sheet_name,
            range_name=range_name
        )
        
        if result.get("error"):
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result["error"]
                    }
                ],
                "isError": True
            }, is_error=True)
        
        clients = result.get("clients", [])
        response_text = f"Retrieved {len(clients)} client(s)\n\n"
        
        if not clients:
            response_text += "No clients found in the sheet."
        else:
            for i, client in enumerate(clients, 1):
                response_text += f"Client {i}:\n"
                for key, value in client.items():
                    response_text += f"  {key}: {value}\n"
                response_text += "\n"
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error getting clients: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


def handle_add_clients(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle addClients tool call."""
    try:
        sheets_client = get_google_sheets_client()
        if not sheets_client:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Google Sheets not configured. Please configure GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_TOKEN_PATH, and GOOGLE_SHEETS_SPREADSHEET_ID"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        clients = arguments.get("clients", [])
        if not clients:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'clients' is required (array of client objects)"
                    }
                ],
                "isError": True
            }, is_error=True)
        
        sheet_name = arguments.get("sheet_name")
        
        result = sheets_client.add_clients(
            clients=clients,
            sheet_name=sheet_name
        )
        
        if result.get("success"):
            response_text = f"✅ {result.get('message', 'Clients added successfully')}\n"
            response_text += f"Added {result.get('added_count', 0)} client(s)"
        else:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Failed to add clients")
                    }
                ],
                "isError": True
            }, is_error=True)
        
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error adding clients: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


async def handle_browser_navigate(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle browser_navigate tool call."""
    try:
        browser_service = get_browser_service()
        url = arguments.get("url", "")
        if not url:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'url' is required for browser navigation"
                    }
                ],
                "isError": True
            }, is_error=True)

        session_id = arguments.get("session_id", "default")
        wait_for = arguments.get("wait_for")

        result = await browser_service.navigate(
            url=url,
            session_id=session_id,
            wait_for=wait_for,
        )

        if result.get("status") == "error":
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Error navigating to {url}: {result.get('error', 'Unknown error')}"
                    }
                ],
                "isError": True
            }, is_error=True)

        response_text = f"✅ Navigated to {result.get('url', url)}\n"
        response_text += f"Title: {result.get('title', 'N/A')}\n"
        response_text += f"Session ID: {result.get('session_id', session_id)}"

        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error navigating browser: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


async def handle_browser_interact(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle browser_interact tool call."""
    try:
        browser_service = get_browser_service()
        action = arguments.get("action", "")
        if not action:
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": "Error: 'action' is required (click, type, submit, scroll, wait)"
                    }
                ],
                "isError": True
            }, is_error=True)

        session_id = arguments.get("session_id", "default")
        selector = arguments.get("selector")
        text = arguments.get("text")

        result = await browser_service.interact(
            action=action,
            selector=selector,
            text=text,
            session_id=session_id,
        )

        if result.get("status") == "error":
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Error performing {action}: {result.get('error', 'Unknown error')}"
                    }
                ],
                "isError": True
            }, is_error=True)

        response_text = f"✅ Successfully performed {action}"
        if selector:
            response_text += f" on {selector}"
        if result.get("result"):
            response_text += f"\nResult: {result.get('result')}"

        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error interacting with browser: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


async def handle_browser_extract(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle browser_extract tool call."""
    try:
        browser_service = get_browser_service()
        extract_type = arguments.get("extract_type", "all")
        selector = arguments.get("selector")
        session_id = arguments.get("session_id", "default")

        result = await browser_service.extract(
            extract_type=extract_type,
            selector=selector,
            session_id=session_id,
        )

        if result.get("status") == "error":
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Error extracting data: {result.get('error', 'Unknown error')}"
                    }
                ],
                "isError": True
            }, is_error=True)

        extracted = result.get("extracted", {})
        response_text = f"✅ Extracted {extract_type} data:\n\n"

        if "title" in extracted:
            response_text += f"Title: {extracted['title']}\n"
        if "url" in extracted:
            response_text += f"URL: {extracted['url']}\n"
        if "text" in extracted:
            text_preview = extracted['text'][:500]
            response_text += f"Text (preview): {text_preview}...\n" if len(extracted['text']) > 500 else f"Text: {text_preview}\n"
        if "links" in extracted:
            links = extracted['links']
            response_text += f"Links found: {len(links)}\n"
            for i, link in enumerate(links[:10], 1):
                response_text += f"  {i}. {link.get('text', '')} -> {link.get('href', '')}\n"
            if len(links) > 10:
                response_text += f"  ... and {len(links) - 10} more links\n"
        if "metadata" in extracted:
            metadata = extracted['metadata']
            response_text += f"Metadata: {len(metadata)} items\n"
            for key, value in list(metadata.items())[:5]:
                response_text += f"  {key}: {value}\n"

        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error extracting from browser: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


async def handle_browser_screenshot(

    arguments: Dict[str, Any],
    make_response: Callable[[Dict[str, Any], bool], Dict[str, Any]],
) -> Dict[str, Any]:
    """Handle browser_screenshot tool call."""
    try:
        browser_service = get_browser_service()
        session_id = arguments.get("session_id", "default")
        full_page = arguments.get("full_page", False)
        selector = arguments.get("selector")

        result = await browser_service.screenshot(
            session_id=session_id,
            full_page=full_page,
            selector=selector,
        )

        if result.get("status") == "error":
            return make_response({
                "content": [
                    {
                        "type": "text",
                        "text": f"Error taking screenshot: {result.get('error', 'Unknown error')}"
                    }
                ],
                "isError": True
            }, is_error=True)

        screenshot_path = result.get("screenshot_path", "")
        screenshot_url = result.get("screenshot_url", "")

        response_text = f"✅ Screenshot captured successfully\n"
        response_text += f"Path: {screenshot_path}\n"
        if screenshot_url:
            response_text += f"URL: {screenshot_url}"

        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        })
    except Exception as e:
        return make_response({
            "content": [
                {
                    "type": "text",
                    "text": f"Error taking screenshot: {str(e)}"
                }
            ],
            "isError": True
        }, is_error=True)


