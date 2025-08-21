export default{
     removeObjectByFieldValue(array, fieldName, value) {
        return array.filter(obj => obj[fieldName] !== value);
    }
}
