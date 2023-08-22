use pyo3::prelude::*;
use pyo3::types::{PyDict, PyTuple, PyList};
use pyo3::wrap_pyfunction;

const DICT: i32 = 0;
const LIST: i32 = 1;
const TUPLE: i32 = 2;
const VALUE: i32 = 3;

fn flatten_structure_helper<'a>(obj: &'a PyAny, tokens: &mut Vec<i32>, keys: &mut Vec<PyObject>, py: Python<'a>) {
    if let Ok(dict) = obj.downcast::<PyDict>() {
        tokens.push(DICT);
        tokens.push(dict.len() as i32);
        for (key, value) in dict.iter() {
            keys.push(key.into_py(py));
            flatten_structure_helper(value, tokens, keys, py);
        }
    } else if let Ok(list) = obj.downcast::<PyList>() {
        tokens.push(LIST);
        tokens.push(list.len() as i32);
        for item in list.iter() {
            flatten_structure_helper(item, tokens, keys, py);
        }
    } else if let Ok(tuple) = obj.downcast::<PyTuple>() {
        tokens.push(TUPLE);
        tokens.push(tuple.len() as i32);
        for item in tuple.iter() {
            flatten_structure_helper(item, tokens, keys, py);
        }
    } else {
        tokens.push(VALUE);
    }
}

pub fn flatten_structure(py: Python, data: &PyAny) -> PyResult<(Vec<i32>, Vec<PyObject>)> {
    let mut tokens: Vec<i32> = Vec::new();
    let mut keys: Vec<PyObject> = Vec::new();
    flatten_structure_helper(data, &mut tokens, &mut keys, py); // Pass PyAny reference
    Ok((tokens, keys))
}

fn flatten_helper<'a>(obj: &'a PyAny, flat_data: &mut Vec<PyObject>, py: Python<'a>) {
    if let Ok(dict) = obj.downcast::<PyDict>() {
        for (_, value) in dict.iter() {
            flatten_helper(value, flat_data, py);
        }
    } else if let Ok(list) = obj.downcast::<PyList>() {
        for item in list.iter() {
            flatten_helper(item, flat_data, py);
        }
    } else if let Ok(tuple) = obj.downcast::<PyTuple>() {
        for item in tuple.iter() {
            flatten_helper(item, flat_data, py);
        }
    } else {
        flat_data.push(obj.to_object(py));
    }
}



fn unflatten_helper<'a>(tokens: &mut std::slice::Iter<'a, i32>, keys: &mut std::slice::Iter<'a, PyObject>, flat_data: &mut std::slice::Iter<'a, PyObject>, py: Python<'a>) -> PyObject {
    let token = *tokens.next().unwrap();
    match token {
        DICT => {
            let n = *tokens.next().unwrap();
            let dict = PyDict::new(py);
            for _ in 0..n {
                let key = keys.next();
                let value = unflatten_helper(tokens, keys, flat_data, py);
                dict.set_item(key, value).unwrap();
            }
            dict.to_object(py)
        }
        LIST => {
            let n = *tokens.next().unwrap();
            let list = PyList::new(py, (0..n).map(|_| unflatten_helper(tokens, keys, flat_data, py)));
            list.to_object(py)
        }
        TUPLE => {
            let n = *tokens.next().unwrap();
            let tuple = PyTuple::new(py, (0..n).map(|_| unflatten_helper(tokens, keys, flat_data, py)));
            tuple.to_object(py)
        }
        VALUE => flat_data.next().unwrap().clone_ref(py),
        _ => py.None(),
    }
}

#[pyclass]
pub struct Flattener {
    tokens: Vec<i32>,
    keys: Vec<PyObject>,
}

#[pymethods]
impl Flattener {
    #[new]
    fn new() -> Self {
        Flattener {
            tokens: Vec::new(),
            keys: Vec::new(),
        }
    }

    fn flatten(&mut self, py: Python, data: PyObject) -> PyResult<Vec<PyObject>> {
        if self.tokens.is_empty() {
            (self.tokens, self.keys) = flatten_structure(py, data.as_ref(py))?; // Assuming flatten_structure returns Vec<StructureElement>
        }
        let mut flat_data = Vec::new();
        flatten_helper(data.as_ref(py), &mut flat_data, py); // Assuming flatten_helper takes appropriate parameters
        Ok(flat_data)
    }

    fn unflatten(&self, py: Python, flat_data: Vec<PyObject>) -> PyResult<PyObject> {
        Ok(unflatten_helper(&mut self.tokens.iter(), &mut self.keys.iter(), &mut flat_data.iter(), py)) // Assuming unflatten_helper takes appropriate parameters
    }
}

#[pymodule]
fn rust_flatten(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Flattener>()?;
    Ok(())
}