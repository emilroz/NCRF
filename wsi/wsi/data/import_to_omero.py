import logging
import json
import os

import omero
import omero.clients

LOGGING_FORMAT = "%(asctime)s %(levelname)-7s [%(name)16s] %(message)s"
LOGGER = logging.getLogger('import-to-omero')

JSON_FILE_EXTENSIONS = [".json"]
JSON_NAME_KEY = "name"
JSON_VERTICES_KEY = "vertices"
JSON_POSITIVE_KEY = "positive"
JSON_NEGATIVE_KEY = "negative"
JSON_LABEL_KEY = "label"

class OmeroImportHelper(object):

    def get_json_list(self, directory):
        json_list = [
            os.path.join(directory, f) for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and
            os.path.splitext(f)[1] in JSON_FILE_EXTENSIONS
        ]
        return json_list

    def get_image_name_dictionary(self, gateway, dataset_id):
        omero_dataset = gateway.getObject('Dataset', dataset_id)
        image_name_dictionary = {}
        for image in omero_dataset.listChildren():
            image_name_dictionary[
                os.path.splitext(image.name)[0]] = image.id
        return image_name_dictionary

    def convert_annotations(self, list_of_annotations, label):
        converted_annotations = []
        for ann in list_of_annotations:
            annotation = {}
            annotation[JSON_NAME_KEY] = ann[JSON_NAME_KEY]
            vertices = [str(el[0]) + "," + str(el[1]) for el in ann[JSON_VERTICES_KEY]]
            vertices = " ".join(vertices)
            annotation[JSON_LABEL_KEY] = label
            annotation[JSON_VERTICES_KEY] = vertices
            converted_annotations.append(annotation)
        return converted_annotations

    def load_json_from_file(self, file_path):
        with open(file_path, 'r') as json_file:
            annotations = json.load(json_file)
        annotation_list = []
        annotation_list.extend(self.convert_annotations(
            annotations[JSON_POSITIVE_KEY], JSON_POSITIVE_KEY))
        annotation_list.extend(self.convert_annotations(
            annotations[JSON_NEGATIVE_KEY], JSON_NEGATIVE_KEY))
        return annotation_list

    def create_polygon_roi(self, gateway, image_id, annotation):
        roi = omero.model.RoiI()
        roi.setName(omero.rtypes.rstring(annotation[JSON_NAME_KEY]))
        roi.setDescription(omero.rtypes.rstring(annotation[JSON_LABEL_KEY]))
        polygon = omero.model.PolygonI()
        polygon.setTextValue(omero.rtypes.rstring(annotation[JSON_NAME_KEY]))
        polygon.setPoints(omero.rtypes.rstring(annotation[JSON_VERTICES_KEY]))
        if annotation[JSON_LABEL_KEY] == JSON_POSITIVE_KEY:
            polygon.setStrokeColor(omero.rtypes.rint(65280))
        else:
            polygon.setStrokeColor(omero.rtypes.rint(-16776961))
        polygon.setFillColor(omero.rtypes.rint(0))
        roi.addShape(polygon)
        roi.setImage(omero.model.ImageI(image_id, False))
        gateway.getUpdateService().saveObject(roi)

    def convert_json_to_omero_annotation(
            self, gateway, file_path, omero_image_name_dictionary):
        file_name = os.path.splitext(os.path.basename(file_path))[0].lower()
        if file_name in omero_image_name_dictionary:
            LOGGER.info("Adding annotations to %s" % file_name)
            annotations = self.load_json_from_file(file_path)
            LOGGER.debug(annotations)
            for annotation in annotations:
                self.create_polygon_roi(
                    gateway, omero_image_name_dictionary[file_name],
                    annotation)
