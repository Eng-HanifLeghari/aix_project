import os
from apps.camera.camera_utils.camera_enums import Threats, Priorities, Red_Force, Blue_Force, ThreatsStrings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, Q
from datetime import date
from rest_framework import status
from apps.camera.models import Camera
from customutils.helpers import provided_datetime_format, default_datetime_format
from datetime import datetime, timedelta


class ElasticSearchHandler:

    def __init__(self):
        self.client = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_IP")])
        self.dynamic_index_part = str(date.today()).replace('-', '_')

    def events_filter_by_ip(self, ip=None):
        search_obj = Search(using=self.client, index=f"{os.getenv('STREAM_INDEX')}*").extra(from_=0, size=10000)
        if ip:
            result = search_obj.filter('match', camera_ip=ip)
        else:
            result = search_obj
        return self.execute_query(result)

    def alerts_filter_by_ip(self, ip=None):
        search_obj = Search(using=self.client, index=f"{os.getenv('ALERT_INDEX')}*").extra(from_=0, size=10000)
        if ip:
            result = search_obj.filter('match', camera_ip=ip)
        else:
            result = search_obj
        return self.execute_query(result)

    def events_aggregation(self, ip=None, camera_name=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {}
        try:
            search_obj = Search(using=self.client, index=f"{os.getenv('ALERT_INDEX')}*").extra(from_=0, size=10000)
            if ip:
                aggregate_dict = {"ip": ip}
                result = search_obj.filter('match', camera_ip=ip)
            else:
                result = search_obj
            bucket_query = A("terms", field='event_no', size=10)
            result.aggs.bucket('event_no', bucket_query)
            aggregated = result.execute().to_dict()
            if aggregated.get("aggregations") is not None:
                for bucket in aggregated.get("aggregations").get("event_no").get("buckets"):
                    aggregate_dict[Threats(bucket.get("key", None)).name] = bucket.get("doc_count", None)
                aggregate_dict["camera_name"] = "Not found in Database" if camera_name is None else camera_name.camera_name
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Record not found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    def threat_alert_aggregation(self, ip=None, start_time=None, end_time=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {"datasets": [{"data": []}], "labels": []}
        default_end_time, default_start_time = default_datetime_format()
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        try:
            search_obj = Search(using=self.client, index=f"{os.getenv('ALERT_INDEX')}*")
            if ip:
                result = search_obj.filter(
                    Q("range", Time={"gte": start_time, "lte": end_time}) &
                    Q("term", camera_ip=ip)
                )
            else:
                result = search_obj.filter(Q("range", Time={"gte": start_time, "lte": end_time}))
            bucket_query = A("terms", field='threat_value', size=5)
            result.aggs.bucket('threat_value', bucket_query)
            aggregated = result.execute().to_dict()
            if aggregated.get("aggregations") is not None:
                for bucket in aggregated.get("aggregations").get("threat_value").get("buckets"):
                    if 0 < bucket.get("key", None) < 10:
                        if Priorities(bucket.get("key", None)).value:
                            aggregate_dict.get("datasets")[0].get("data").append(bucket.get("doc_count", None))
                            aggregate_dict.get("labels").append(Priorities(bucket.get("key", None)).name)
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Record not found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    def force_alert_aggregation(self, ip=None, start_time=None, end_time=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {"datasets": [{"backgroundColor": "red", "type": "bar", "label": "Red Force", "data": []},
                                       {"backgroundColor": "blue", "type": "bar", "label": "Blue Force", "data": []}],
                          "labels": []}
        default_end_time, default_start_time = default_datetime_format()
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        es = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_IP")])
        try:
            if not ip:
                query = {
                    "size": 0,
                    "query": {
                        "bool": {
                            "filter": [
                                {
                                    "range": {
                                        "Time": {
                                            "gte": start_time,
                                            "lte": end_time
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "date_buckets": {
                            "date_histogram": {
                                "field": "date",
                                "fixed_interval": "1d",
                                "format": "yyyy-MM-dd"
                            },
                            "aggs": {
                                "force_buckets": {
                                    "terms": {
                                        "field": "force.keyword"
                                    }
                                }
                            }
                        }
                    }
                }
            else:
                query = {
                    "size": 30,
                    "query": {
                        "bool": {
                            "must": [
                                {"exists": {"field": "camera_ip"}}
                            ],
                            "filter": [
                                {
                                    "range": {
                                        "Time": {
                                            "gte": start_time,
                                            "lte": end_time
                                        }
                                    }
                                },
                                {"term": {"camera_ip": ip}}
                            ]
                        }
                    },
                    "aggs": {
                        "date_buckets": {
                            "date_histogram": {
                                "field": "date",
                                "fixed_interval": "1d",
                                "format": "yyyy-MM-dd"
                            },
                            "aggs": {
                                "force_buckets": {
                                    "terms": {
                                        "field": "force.keyword"
                                    }
                                }
                            }
                        }
                    }
                }
            result = es.search(index=f"{os.getenv('ALERT_INDEX')}*", body=query)
            if result.get("aggregations") is not None:
                for date_bucket in result.get("aggregations").get("date_buckets").get("buckets"):
                    try:
                        if date_bucket.get("force_buckets").get("buckets")[0].get("key") == "red_force":
                            aggregate_dict.get("datasets")[0].get("data").append(
                                date_bucket.get("force_buckets").get("buckets")[0].get("doc_count"))
                    except:
                        aggregate_dict.get("datasets")[0].get("data").append(0)
                    try:
                        if date_bucket.get("force_buckets").get("buckets")[1].get("key") == "blue_force":
                            aggregate_dict.get("datasets")[1].get("data").append(
                                date_bucket.get("force_buckets").get("buckets")[1].get("doc_count"))
                    except:
                        aggregate_dict.get("datasets")[1].get("data").append(0)
                    date_format = datetime.strptime(date_bucket["key_as_string"], "%Y-%m-%d").strftime(
                        os.getenv("CUSTOM_DATE_FORMAT"))
                    aggregate_dict.get("labels").append(date_format)
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Record Not Found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": False,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            es.transport.close()
            return aix_response

    def asset_count_aggregation(self, ip=None, start_time=None, end_time=None, required_cameras=None,
                                required_events=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {"datasets": [], "labels": []}
        default_end_time, default_start_time = default_datetime_format()
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        es = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_IP")])
        try:
            query = {
                "size": 0,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "Time": {
                                        "gte": start_time,
                                        "lte": end_time
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "date_buckets": {
                        "date_histogram": {
                            "field": "date",
                            "fixed_interval": "1d",
                            "format": "yyyy-MM-dd"
                        },
                        "aggs": {
                            "ip_buckets": {
                                "terms": {
                                    "field": "camera_ip.keyword"
                                },
                                "aggs": {
                                    "event_bucket": {
                                        "terms": {
                                            "field": "event_no"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            result = es.search(index=f"{os.getenv('ALERT_INDEX')}*", body=query)
            cameras = Camera.objects.select_related("user_name", "service_type").filter(ip__in=required_cameras).values(
                "ip", "camera_name")
            aggregate_dict["datasets"] = [{"ip": camera["ip"], "label":f"{ThreatsStrings[threat.name].value}({camera['camera_name']})", "value": threat.value, "data": []}
                                          for camera in cameras for threat in Threats if
                                          threat.value in required_events]
            labels = set([key["ip"] for key in aggregate_dict.get("datasets")])
            if result.get("aggregations") is not None:
                for bucket in result.get("aggregations").get("date_buckets").get("buckets"):
                    for cam_ip in bucket.get("ip_buckets").get("buckets"):
                        if cam_ip.get("key") in labels:
                            for event in cam_ip.get("event_bucket").get("buckets"):
                                for event_no in aggregate_dict.get("datasets"):
                                    if cam_ip.get("key") == event_no.get("ip") and event.get("key") == event_no.get(
                                            "value"):
                                        event_no.get("data").append(event["doc_count"])
                                        break
                    date_format = datetime.strptime(bucket["key_as_string"], "%Y-%m-%d").strftime(os.getenv("CUSTOM_DATE_FORMAT"))
                    aggregate_dict.get("labels").append(date_format)
                    for item in aggregate_dict.get("datasets"):
                        if len(item.get("data")) < len(aggregate_dict.get("labels")):
                            item.get("data").append(0)
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Record not found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            es.transport.close()
            return aix_response

    def force_count_aggregation(self, start_time=None, end_time=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = []
        default_end_time, default_start_time = default_datetime_format()
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        es = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_IP")])
        try:
            query = {
                "size": 0,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "Time": {
                                        "gte": start_time,
                                        "lte": end_time
                                    }
                                }
                            },
                        ]
                    }
                },
                "aggs": {
                    "by_camera_ip": {
                        "terms": {
                            "field": "camera_ip.keyword"
                        },
                        "aggs": {
                            "by_force": {
                                "terms": {
                                    "field": "force.keyword"
                                }
                            }
                        }
                    }
                }
            }
            result = es.search(index=f"{os.getenv('ALERT_INDEX')}*", body=query)
            cameras = Camera.objects.select_related("user_role", "service_type") \
                .values("ip", "camera_name", "lat", "lng", "active_status")
            if result.get("aggregations") is not None:
                for bucket in result.get("aggregations").get("by_camera_ip").get("buckets"):
                    camera = cameras.filter(ip=bucket.get("key")).first()
                    if camera:
                        camera["red_force"] = 0
                        camera["blue_force"] = 0
                        for force in bucket.get("by_force").get("buckets"):
                            try:
                                if force.get("key", "") == "red_force":
                                    camera["red_force"] = force.get("doc_count")
                                if force.get("key", "") == "blue_force":
                                    camera["blue_force"] = force.get("doc_count")
                            except:
                                pass
                        aggregate_dict.append(camera)
                        cameras = cameras.exclude(ip=camera.get("ip"))
                for camera in cameras:
                    camera["red_force"] = 0
                    camera["blue_force"] = 0
                    aggregate_dict.append(camera)
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Record not found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            es.transport.close()
            return aix_response

    def legend_count_aggregation(self, camera_ip=None, start_time=None, end_time=None, force=[]):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {"ip": camera_ip, "red_force": 0, "blue_force": 0}
        default_end_time, default_start_time = default_datetime_format()
        camera_ip = camera_ip if camera_ip else "192.168.23.157"
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        try:
            result = Search(using=self.client, index=f"{os.getenv('ALERT_INDEX')}*")
            result = result.filter(
                Q("range", Time={"gte": start_time, "lte": end_time}) &
                Q("term", camera_ip=camera_ip)
            )
            bucket_query = A("terms", field='event_no', size=10)
            result.aggs.bucket('event_no', bucket_query)
            aggregated = result.execute().to_dict()
            red_force = [key.value for key in Red_Force]
            blue_force = [key.value for key in Blue_Force]
            if aggregated.get("aggregations") is not None:
                for bucket in aggregated.get("aggregations").get("event_no").get("buckets"):
                    if bucket.get("key") in force:
                        if bucket.get("key") in red_force:
                            aggregate_dict[Red_Force(bucket.get("key", None)).name] = bucket.get("doc_count", None)
                            aggregate_dict["red_force"] = aggregate_dict["red_force"] + bucket.get("doc_count", None)
                        if bucket.get("key") in blue_force:
                            aggregate_dict[Blue_Force(bucket.get("key", None)).name] = bucket.get("doc_count", None)
                            aggregate_dict["blue_force"] = aggregate_dict["blue_force"] + bucket.get("doc_count", None)
                aix_response = {
                        "statusMessage": "Query searched successfully!",
                        "data": aggregate_dict,
                        "statusCode": status.HTTP_200_OK,
                        "errorStatus": False,
                    }
            else:
                aix_response = {
                        "statusMessage": "Data not found!",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": True,
                    }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    def image_alert_path(self, alert_id=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        try:
            result = Search(using=self.client, index=f"{os.getenv('STREAM_IMAGE_ALERT')}*")
            if alert_id:
                result = result.query(
                    Q("term", alert_id=alert_id)
                )
            else:
                aix_response = {
                        "statusMessage": "Alert ID not found in Query Parameters",
                        "data": [],
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorStatus": False,
                    }
                return aix_response
            data = self.execute_query(result)
            aix_response = {
                    "statusMessage": "Query searched successfully!",
                    "data": data,
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    def image_alert_aggregation(self, camera_ip=None, start_time=None, end_time=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        current_datetime = datetime.now()
        default_start_time, default_end_time = (current_datetime - timedelta(days=1)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"), current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        # start_time, end_time = provided_datetime_format(start_time, end_time)
        start_time = start_time if start_time else default_start_time
        end_time = end_time if end_time else default_end_time
        try:
            result = Search(using=self.client, index=f"{os.getenv('STREAM_IMAGE_ALERT')}*").extra(from_=0, size=10000)
            if camera_ip:
                result = result.query(
                    Q("range", Time={"gte": start_time, "lte": end_time}) &
                    Q("term", camera_ip=camera_ip)
                )
            else:
                result = result.query(Q("range", Time={"gte": start_time, "lte": end_time}))
            data = self.execute_query(result)
            aix_response = {
                    "statusMessage": "Query searched successfully!",
                    "data": data,
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            return aix_response

    def single_page_graph_aggregation(self, ip=None, required_events=None):
        aix_response = dict(statusMessage="", data=[], errorStatus=False, statusCode=200)
        aggregate_dict = {"datasets": [], "labels": []}
        custom_time_format = os.getenv("CUSTOM_TIME_FORMAT")
        current_datetime = datetime.now()
        start_time, end_time = (current_datetime - timedelta(days=1)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"), current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        es = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_IP")])
        try:
            query = {
                  "size": 0,
                  "query": {
                    "bool": {
                      "filter": [
                        {
                          "range": {
                            "Time": {
                              "gte": start_time,
                              "lte": end_time
                            }
                          }
                        },
                        {
                          "term": {
                            "camera_ip.keyword": ip
                          }
                        }
                      ]
                    }
                  },
                  "aggs": {
                    "hour_buckets": {
                      "date_histogram": {
                        "field": "Time",
                        "calendar_interval": "hour",
                        "format": "yyyy-MM-dd HH:mm:ss"
                      },
                      "aggs": {
                        "event_bucket": {
                          "terms": {
                            "field": "event_no"
                          }
                        }
                      }
                    }
                  }
                }
            result = es.search(index=f"{os.getenv('ALERT_INDEX')}*", body=query)
            cameras = Camera.objects.select_related("user_name", "service_type").filter(
                ip=ip).values("ip", "camera_name")
            aggregate_dict["datasets"] = [{"ip": camera["ip"], "label": ThreatsStrings[threat.name].value, "value": threat.value, "data": []}
                                          for camera in cameras for threat in Threats if
                                          threat.value in required_events]
            for bucket in result.get("aggregations").get("hour_buckets").get("buckets"):
                for event_key in bucket.get("event_bucket").get("buckets"):
                    for event_no in aggregate_dict.get("datasets"):
                        if event_key.get("key") == event_no.get("value"):
                            event_no.get("data").append(event_key["doc_count"])
                            break
                time_format = datetime.strptime(bucket["key_as_string"], "%Y-%m-%d %H:%M:%S").strftime(custom_time_format)
                aggregate_dict.get("labels").append(time_format)
                for item in aggregate_dict.get("datasets"):
                    if len(item.get("data")) < len(aggregate_dict.get("labels")):
                        item.get("data").append(0)
            aix_response = {
                    "statusMessage": "Query searched successfully!",
                    "data": aggregate_dict,
                    "statusCode": status.HTTP_200_OK,
                    "errorStatus": False,
                }
        except Exception as e:
            aix_response = {
                    "statusMessage": str(e),
                    "data": [],
                    "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "errorStatus": True,
                }
        finally:
            es.transport.close()
            return aix_response

    def execute_query(self, result):
        response = result.execute(result)
        return self.query_response(response)

    def query_response(self, response):
        response = response.to_dict()
        end_result = []
        for res in response['hits']['hits']:
            res.get("_source")["Time"] = datetime.strptime(res.get("_source").get("Time"), "%Y-%m-%d %H:%M:%S.%f").strftime(os.getenv("CUSTOM_TIME_FORMAT"))
            end_result.append(res['_source'])
        return end_result
