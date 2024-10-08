import os
import onnx
import argparse
import model_editor


def split_cnnx(args):
    # 'num_layers' is the number of repeated layers in the model architecture.
    num_layers = args.n_layers
    model_path = args.model
    encoding_path = args.encoding
    split_output_model_path = os.path.join(os.path.dirname(model_path) + "_split")

    # `onnx.shape_inference` process before splitting an ONNX model
    #    - It is required to run onnx.shape_inference process before splitting an ONNX model.
    #    - For more details, please refer to this documentation: https://onnx.ai/onnx/api/shape_inference.html
    shape_infered_model_path = os.path.join(
        os.path.dirname(model_path) + "/shape_infered_model.onnx"
    )
    onnx.shape_inference.infer_shapes_path(model_path, shape_infered_model_path)

    model = model_editor.CnnxModel.load_model(
        shape_infered_model_path, encoding_path=encoding_path
    )
    model.graph.update_ignore_node_quantization()
    model.graph.remove_ignore_node_quantization()

    for i in range(0, num_layers + 1):
        print("=" * 50, "layer", i, "split", "=" * 50)

        add_nodes = set()
        exclude_nodes = set()

        for node in model.nodes:
            if "layers" in node.name:
                if (
                    ("self_attn/Cast_3" in node.name)
                    or ("self_attn/Cast_5" in node.name)
                    or ("self_attn/Cast_4" in node.name)
                    or ("self_attn/Cast_6" in node.name)
                    or ("self_attn/Cast_9" in node.name)
                ):
                    add_nodes.add(node.name)
                else:
                    if f"layers.{i}/" in node.name:
                        add_nodes.add(node.name)
                    else:
                        exclude_nodes.add(node.name)
            else:
                add_nodes.add(node.name)

        if i < num_layers:
            add_nodes.remove("/model/norm/org_module/Cast")
            add_nodes.remove("/model/norm/org_module/Pow")
            add_nodes.remove("/model/norm/org_module/ReduceMean")
            add_nodes.remove("/model/norm/org_module/Add")
            add_nodes.remove("/model/norm/org_module/Sqrt")
            add_nodes.remove("/model/norm/org_module/Div")
            add_nodes.remove("/model/norm/org_module/Mul")
            add_nodes.remove("/model/norm/org_module/Cast_1")
            add_nodes.remove("/model/norm/org_module/Mul_1")
            add_nodes.remove("/lm_head/org_module/Transpose")
            add_nodes.remove("/lm_head/org_module/MatMul")
            add_nodes.remove("/Cast")
            exclude_nodes.add("/model/norm/org_module/Cast")
        for j in range(i + 1, num_layers):
            add_nodes.remove(f"/model/layers.{j}/self_attn/Cast_3")
            add_nodes.remove(f"/model/layers.{j}/self_attn/Cast_5")
            add_nodes.remove(f"/model/layers.{j}/self_attn/Cast_4")
            add_nodes.remove(f"/model/layers.{j}/self_attn/Cast_6")
            add_nodes.remove(f"/model/layers.{j}/self_attn/Cast_9")
            exclude_nodes.add(f"/model/layers.{j}/self_attn/Cast_3")
            exclude_nodes.add(f"/model/layers.{j}/self_attn/Cast_5")
            exclude_nodes.add(f"/model/layers.{j}/self_attn/Cast_4")
            exclude_nodes.add(f"/model/layers.{j}/self_attn/Cast_6")
            exclude_nodes.add(f"/model/layers.{j}/self_attn/Cast_9")
        # In this case, start nodes is the start node of the model you want to cut, end nodes is the last node,
        # and finally 'exclude_nodes' is the nodes that is not related to the path from the 'start_nodes' to the 'end_nodes'.
        if i < num_layers:
            start_nodes = list(add_nodes)
            end_nodes = [f"/model/layers.{i}/Add_1"]
            exclude_nodes = list(exclude_nodes)
        else:
            start_nodes = [
                "/model/norm/org_module/Cast",
                "/lm_head/org_module/Transpose",
            ]
            end_nodes = ["/Cast"]
            exclude_nodes = []

        nodes = model.graph.nodes.find_all_nodes_between(
            start_nodes, end_nodes, exclude_nodes
        )
        graph = model_editor.CnnxGraph(name="graph", nodes=nodes, inputs=[], outputs=[])
        graph.ordering_info = model.graph.ordering_info
        new_model = model_editor.CnnxModel(graph=graph, properties=model.properties)

        if not os.path.exists(split_output_model_path):
            os.makedirs(split_output_model_path)
        output_encoding_path = os.path.join(split_output_model_path, "encodings")
        if not os.path.exists(output_encoding_path):
            os.makedirs(output_encoding_path)
        new_model.save_model(
            os.path.join(split_output_model_path + f"/layer_{i:02}.onnx"),
            encoding_path=os.path.join(output_encoding_path, f"layer_{i:02}.encodings"),
        )


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--n_layers", type=int, default=28)
    argparser.add_argument(
        "--model",
        type=str,
        default="./models/cnnx/IP/model_ip.onnx",
    )
    argparser.add_argument(
        "--encoding",
        type=str,
        default="./models/cnnx/IP/model_ip.encodings",
    )
    args = argparser.parse_args()

    split_cnnx(args)


if __name__ == "__main__":
    main()
