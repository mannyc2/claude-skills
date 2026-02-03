#!/usr/bin/env bash

# Typst Compilation Helper Script
# Purpose: Compile .typ files to PDF and optionally convert to images
# Usage: ./compile-typst.sh <file.typ> [--image] [--format png|jpg]

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_IMAGE_FORMAT="png"
DEFAULT_DPI=300

# ============================================================================
# Colors for output
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_error() {
    echo -e "${RED}ERROR:${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

usage() {
    cat << EOF
Typst Compilation Helper

USAGE:
    $0 <file.typ> [OPTIONS]

OPTIONS:
    --image             Also convert PDF to image(s)
    --format FORMAT     Image format: png, jpg (default: png)
    --dpi DPI          Image resolution (default: 300)
    --output DIR       Output directory (default: same as input file)
    --help             Show this help message

EXAMPLES:
    # Compile to PDF only
    $0 cheatsheet.typ

    # Compile to PDF and PNG images
    $0 cheatsheet.typ --image

    # Compile to PDF and high-res JPG
    $0 cheatsheet.typ --image --format jpg --dpi 600

    # Compile to specific output directory
    $0 cheatsheet.typ --output ./output

REQUIREMENTS:
    - typst CLI (install: brew install typst or cargo install typst-cli)
    - imagemagick (for --image option: brew install imagemagick)

EOF
}

check_dependencies() {
    local missing=()

    # Check for typst
    if ! command -v typst &> /dev/null; then
        missing+=("typst")
    fi

    # Check for convert (ImageMagick) if image conversion requested
    if [[ "$CONVERT_TO_IMAGE" == "true" ]] && ! command -v convert &> /dev/null; then
        missing+=("imagemagick")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing required dependencies: ${missing[*]}"
        echo ""
        echo "Install with:"
        for dep in "${missing[@]}"; do
            case "$dep" in
                typst)
                    echo "  - Homebrew: brew install typst"
                    echo "  - Cargo: cargo install typst-cli"
                    echo "  - Download: https://github.com/typst/typst/releases"
                    ;;
                imagemagick)
                    echo "  - Homebrew: brew install imagemagick"
                    echo "  - APT: sudo apt install imagemagick"
                    ;;
            esac
        done
        return 1
    fi

    return 0
}

compile_to_pdf() {
    local input_file="$1"
    local output_file="$2"

    print_info "Compiling $input_file to PDF..."

    if typst compile "$input_file" "$output_file"; then
        print_success "PDF created: $output_file"

        # Show file size
        local size=$(du -h "$output_file" | cut -f1)
        print_info "File size: $size"

        return 0
    else
        print_error "Compilation failed"
        return 1
    fi
}

convert_to_image() {
    local pdf_file="$1"
    local output_base="$2"
    local format="$3"
    local dpi="$4"

    print_info "Converting PDF to $(echo "$format" | tr '[:lower:]' '[:upper:]') (${dpi} DPI)..."

    # Get page count
    local page_count=$(pdfinfo "$pdf_file" 2>/dev/null | grep -oP 'Pages:\s+\K\d+' || echo "unknown")

    if [[ "$page_count" == "unknown" ]]; then
        print_warning "Could not determine page count (pdfinfo not available)"
        page_count=1
    fi

    # Convert each page
    if [[ "$page_count" -eq 1 ]]; then
        # Single page - no page number in filename
        local output_file="${output_base}.${format}"

        if convert -density "$dpi" "$pdf_file" -quality 95 "$output_file"; then
            print_success "Image created: $output_file"
            local size=$(du -h "$output_file" | cut -f1)
            print_info "File size: $size"
        else
            print_error "Image conversion failed"
            return 1
        fi
    else
        # Multiple pages - add page numbers
        local output_pattern="${output_base}-%d.${format}"

        if convert -density "$dpi" "$pdf_file" -quality 95 "$output_pattern"; then
            print_success "Images created: ${output_base}-*.${format}"
            print_info "Pages: $page_count"

            # List generated files
            for img in "${output_base}"-*.${format}; do
                if [[ -f "$img" ]]; then
                    local size=$(du -h "$img" | cut -f1)
                    print_info "  - $(basename "$img") ($size)"
                fi
            done
        else
            print_error "Image conversion failed"
            return 1
        fi
    fi

    return 0
}

# ============================================================================
# Main Script
# ============================================================================

# Parse arguments
INPUT_FILE=""
CONVERT_TO_IMAGE=false
IMAGE_FORMAT="$DEFAULT_IMAGE_FORMAT"
IMAGE_DPI="$DEFAULT_DPI"
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --image)
            CONVERT_TO_IMAGE=true
            shift
            ;;
        --format)
            IMAGE_FORMAT="$2"
            shift 2
            ;;
        --dpi)
            IMAGE_DPI="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -*)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [[ -z "$INPUT_FILE" ]]; then
                INPUT_FILE="$1"
            else
                print_error "Multiple input files specified"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate input file
if [[ -z "$INPUT_FILE" ]]; then
    print_error "No input file specified"
    usage
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    print_error "Input file not found: $INPUT_FILE"
    exit 1
fi

if [[ ! "$INPUT_FILE" =~ \.typ$ ]]; then
    print_error "Input file must have .typ extension"
    exit 1
fi

# Validate image format
if [[ ! "$IMAGE_FORMAT" =~ ^(png|jpg|jpeg)$ ]]; then
    print_error "Invalid image format: $IMAGE_FORMAT (must be png, jpg, or jpeg)"
    exit 1
fi

# Normalize jpeg to jpg
if [[ "$IMAGE_FORMAT" == "jpeg" ]]; then
    IMAGE_FORMAT="jpg"
fi

# Check dependencies
if ! check_dependencies; then
    exit 1
fi

# Determine output directory
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR=$(dirname "$INPUT_FILE")
fi

# Create output directory if it doesn't exist
if [[ ! -d "$OUTPUT_DIR" ]]; then
    print_info "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Get base filename without extension
BASENAME=$(basename "$INPUT_FILE" .typ)
OUTPUT_BASE="${OUTPUT_DIR}/${BASENAME}"

# Compile to PDF
PDF_FILE="${OUTPUT_BASE}.pdf"
if ! compile_to_pdf "$INPUT_FILE" "$PDF_FILE"; then
    exit 1
fi

# Convert to image if requested
if [[ "$CONVERT_TO_IMAGE" == "true" ]]; then
    if ! convert_to_image "$PDF_FILE" "$OUTPUT_BASE" "$IMAGE_FORMAT" "$IMAGE_DPI"; then
        exit 1
    fi
fi

# Summary
echo ""
print_success "Compilation complete!"
echo ""
echo "Generated files:"
echo "  - PDF: $PDF_FILE"

if [[ "$CONVERT_TO_IMAGE" == "true" ]]; then
    echo "  - Images: ${OUTPUT_BASE}*.${IMAGE_FORMAT}"
fi

echo ""
print_info "To view PDF: open \"$PDF_FILE\""

exit 0
